from typing import Dict, List, Mapping
import pandas as pd
import json
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
import os
import requests
import yfinance as yf
from dotenv import load_dotenv
import sqlalchemy as sa
import uuid as _uuid
from db_structure.json_encoder import JsonEncoder; 
from db_structure.sql_meta import StockMeta
from werkzeug import Request
from datetime import datetime
import psycopg2
import waitress

load_dotenv()

if 'alphaVantageKey' not in os.environ:
    print('Missing key')
else:
    alphaVantageKey = os.environ['alphaVantageKey']

app = Flask(__name__, static_folder='../frontend/assets',
                        template_folder = "../frontend/")
CORS(app)

dataTickers = {}

class StockImporter:
    def __init__(self) -> None:
        self.db = sa.create_engine(os.environ.get('DB_STRING'))
        self.meta = StockMeta()

        self.meta.meta.create_all(self.db)

        pass

    def create_account(self, uuid = str(_uuid.uuid4())) -> str:
        newrow = self.meta.users.insert()
        newrow = newrow.values(id=uuid)

        with self.db.connect() as conn:
            if conn.execute(self.meta.users.select().where(self.meta.users.c.id == uuid)).fetchone() == None:
                res = conn.execute(newrow)
                conn.commit()
        
        return uuid
    
    def login(self, uuid) -> bool:
        meta = self.meta
        findrow = meta.users.select().where(meta.users.c.id == uuid)
        with self.db.connect() as conn:
            res = conn.execute(findrow)
            try:
                return type(res.fetchone()[0]) == str
            except:
                return False
        
    def getLastQuote(self, ticker: str) -> float | None:
        # Get random number if development mode is on
        if os.getenv('PYTHON_ENV') == 'development':
            from random import  SystemRandom
            return SystemRandom().uniform(50, 150)
        
        # Try to return cached data
        elif ticker in dataTickers:
            return dataTickers[ticker]
        
        # Refresh with new (hydrated) data
        else:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={alphaVantageKey}'

            r = requests.get(url)
            data = r.json()

            try:
                dataTickers[ticker] = data['Global Quote']['05. price']
                return data['Global Quote']['05. price']
            except Exception as e:
                print(e)
                return None

    def getMetaData(self, list) -> yf.Tickers:
        # Get metadata
        ticks = ' '.join(list)

        tickers = yf.Tickers(ticks)

        return tickers

    def handleCsv(self, file) -> pd.DataFrame:

        df = pd.read_csv(file)

        metadata = {
            # Vanguard sp500
            'IE00B3XXRP09': 'VUSA.AS',
            # Van Eck Morningstar
            'NL0011683594': 'TDIV.AS',
            # Abn Amro
            'NL0011540547': 'ABN.AS',
            # ING
            'NL0011821202': 'INGA.AS',
            # Prysmian
            'IT0004176001': 'PRY.MI'
        }

        df['Ticker'] = df['ISIN'].apply(lambda x: None if x not in metadata else metadata[x])
        
        meta = self.getMetaData(df['ISIN'].unique())
        print(meta)
        def TickerCurrentPrice(x):
            qte = self.getLastQuote(x)
            if qte == None:
                try:
                    tk = meta.tickers[x].get_info()
                    return tk['currentPrice']
                except Exception: 
                    print(x)
                    return -10
            else:
                return qte

        df['Cost'] = df['Transactiekosten en/of'].apply(lambda x: 0 if x == "" else x)
        df['Koers'] = df['Ticker'].apply(lambda x: float(TickerCurrentPrice(x)))
        
        df['totalValue'] = (df['Aantal'] * df['Koers']) + (df['Aantal'] * df['Cost'])
        df['currentValue'] = df['Koers'] * df['Aantal']

        
        df = df.loc[:, ['Datum'
                        # ,'Tijd'
                        ,'Product'
                        # ,'ISIN'
                        ,'Ticker'
                        # ,'Beurs'
                        # ,'Uitvoeringsplaats'
                        ,'Aantal'
                        ,'Koers'
                        ,'Waarde'
                        ,'Cost'
                        # ,'Totaal'
                        # ,'Order ID'
                        ,'totalValue'
                        ,'currentValue']]
        df.astype({
            'Cost': 'float'
        })

        df = df.groupby(
            by=['Product', 'Ticker']
        ).aggregate({
            'totalValue': 'sum',
            'currentValue': 'sum',
            'Aantal': 'sum'
        }).reset_index()

        # df['GAK'] = df['totalValue'] / df['Aantal']

        return df

    def get_stocks(self, user_id = None, df = None):
        
        if user_id != None:
            with self.db.connect() as conn:
                rec = self.meta.share_info.select().where(self.meta.share_info.c.user_id == user_id).compile().statement
                df = pd.read_sql(rec, con=conn)
        elif df == None:
            df = pd.DataFrame()

        meta = self.getMetaData(df['ticker'].unique())
        
        def TickerCurrentPrice(x):
            qte = self.getLastQuote(x)
            if qte == None:
                try:
                    tk = meta.tickers[x].get_info()
                    return tk['currentPrice']
                except Exception: 
                    print(x)
                    return -10
            else:
                return qte

        df['Cost'] = 0 #df['Transactiekosten en/of'].apply(lambda x: 0 if x == "" else x)
        df['Koers'] = df['ticker'].apply(lambda x: float(TickerCurrentPrice(x)))
        
        df['totalValue'] = (df['aantal'] * df['Koers']) + (df['aantal'] * 0)
        df['currentValue'] = df['Koers'] * df['aantal']

        
        df = df.loc[:, ['datum'
                        # ,'Tijd'
                        ,'description'
                        # ,'ISIN'
                        ,'ticker'
                        # ,'Beurs'
                        # ,'Uitvoeringsplaats'
                        ,'aantal'
                        ,'Koers'
                        # ,'Totaal'
                        # ,'Order ID'
                        ,'totalValue'
                        ,'currentValue']]
        # df.astype({
        #     'Cost': 'float'
        # })

        df = df.groupby(
            by=['description', 'ticker']
        ).aggregate({
            'totalValue': 'sum',
            'currentValue': 'sum',
            'aantal': 'sum'
        }).reset_index()

        # df['GAK'] = df['totalValue'] / df['Aantal']

        return df

    def group_by(self, colname: str, df: pd.DataFrame) -> pd.DataFrame:
        df2 = df
        
        meta = self.getMetaData(df2['ticker'].unique())
        
        df2 = df2[df2['aantal'] > 0]
        if colname not in df.columns:
            def getGrouping(x):
                try:
                    return meta.tickers[x].info[colname]
                except KeyError:
                    return 'Other'
            df2[colname] = df2['ticker'].apply(lambda x: getGrouping(x))
        
        # Get unique values
        df2 = df2.groupby(
            by=colname
        ).aggregate({
            'currentValue': 'sum',
            'aantal': 'sum'
        }).reset_index()

        df2['percentage'] =  df2['currentValue'] / sum(df2['currentValue'])

        
        # Fix rounding
        df2['currentValue'] = df2['currentValue'].round(4)
        df2['percentage'] = df2['percentage'].round(4)

        return df2

    def addShares(self, file, userid = None):
        df = pd.read_csv(file)

        # Rename spaces
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.lower()

        # Fix Date column
        df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: datetime.strptime(x, '%d-%m-%Y'))
        
        df2 = df.iloc[:, [0,2,3,6]]

        df2.loc[:, 'id'] = [str(_uuid.uuid4()) for _ in range(len(df.index))]
        df2.loc[:, 'ticker'] = None
        df2.loc[:, 'user_id'] = userid

        df2.columns = ['datum', 'description', 'isin', 'aantal', 'id', 'ticker', 'user_id']

        inserts = df2.to_dict(orient='records')

        if userid != None:
            with self.db.connect() as conn:
                conn.execute(self.meta.share_info.insert(),
                         inserts)
                conn.commit()
            return self.get_stocks(userid)
        else:
            return self.get_stocks(None, pd.DataFrame(inserts))

@app.route('/')
def serveIndex():
    return render_template('index.html')

@app.route('/assets')
def serveAssets():
        return app.send

@app.route('/health')
def health():
    return Response('OK', 'text/plain')

@app.route('/dataframe')
def dataframe():
    ex = yf.Ticker('ABN.AS').get_info()

    d = {}
    for i in dict(ex).keys():
        if isinstance(ex[i], str) and 'ABN' not in ex[i]:
            d[i] = ex[i] 

    return Response(json.dumps(list(d.keys()), indent=4), content_type='application/json')

@app.route('/purge', methods=['POST'])
def purge():
    global dataTickers
    dataTickers = {}
    return Response('OK')

@app.route('/dataframe/<groupby>', methods = ['POST'])
def dataframeGroupBy(groupby: str):
    si = StockImporter()

    f = request.files['file']
    df = si.handleCsv(f)
        
    res = si.groupBy(groupby, df).to_dict(orient='records')

    return Response(json.dumps(res), content_type='application/json')

@app.route('/stocks/<groupby>', methods = ['GET'])
def stocks_groupby(groupby: str):
    si = StockImporter()
    df = si.get_stocks(request.headers.get('x-userid'))
    res = si.group_by(groupby, df)

    return Response(res.to_json(orient='records'), content_type='application/json')

@app.route('/stocks/anonymous/<groupby>', methods = ['POST'])
def add_shares_anonymous(groupby: str):
    si = StockImporter()

    f = request.files['file']
    res = si.addShares(f, None)
    res = si.group_by(groupby, pd.DataFrame(res))    
    return Response(JsonEncoder().encode(res), content_type='application/json')

@app.route('/add-shares', methods = ['POST'])
def add_shares():
    si = StockImporter()
    me = StockMeta()
    me = me.getMeta()

    if si.login(request.headers.get('x-userid')) == False:
        return Response(None, status=403)

        
    f = request.files['file']
    res = si.addShares(f, request.headers.get('x-userid'))
    return Response(JsonEncoder().encode(res), content_type='application/json')


@app.route('/create-account', methods=['POST'])
def create_account():
    imp = StockImporter()
    guid = imp.create_account()

    return Response(json.dumps({
        'uuid': guid[0]
    }), content_type='application/json')

@app.route('/login', methods=['POST'])
def check_auth():
    imp = StockImporter()
    res = imp.login(request.headers.get('x-userid'))
    if res:
        return Response(json.dumps({
            'success': res
        }), content_type='application/json')
    else:
        return Response(json.dumps({
             'success': res
        }), status=403 ,content_type='application/json')
    

# Run this on startup
def init():
    si = StockImporter()
    si.create_account(os.environ.get('OWNER_GUID'))
    
init()
