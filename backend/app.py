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
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

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
        '''
        Returns a dataframe with the columns: date, description, isin, market, order_id, count
        '''

        df = pd.read_csv(file)

        df = df.loc[:, [ 'Datum'
                        ,'Product'
                        ,'ISIN'
                        ,'Beurs'
                        ,'Order ID'
                        ,'Aantal' ]]
        
        df.columns = [ 'date', 'description', 'isin' ,'market', 'order_id', 'count' ]

        self.cleaned_csv = df

        return df

    def get_stocks(self, user_id = None, df = None, by: List | str = ['description', 'ticker']):
        
        if user_id != None:
            with self.db.connect() as conn:
                stm = sa.sql.text("select si.*, su.count from share_info si inner join share_user su on si.id = su.share_id and coalesce(si.ticker, '') <> '' and su.user_id = :user_id ")
                
                stm = stm.bindparams(user_id=user_id)
                df = pd.read_sql(stm, con=conn)
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

        df['Koers'] = df['ticker'].apply(lambda x: float(TickerCurrentPrice(x)))
        
        df['totalValue'] = (df['count'] * df['Koers'])
        
        if type(by) == str: by = [by]

        for it in by:
            if it not in df.columns:
                def getGrouping(x):
                    try:
                        return meta.tickers[x].info[it]
                    except KeyError:
                        return 'Other'
                df[it] = df['ticker'].apply(lambda x: getGrouping(x))


        df = df.groupby(
            by=by
        ).aggregate({
            'totalValue': 'sum',
            'count': 'sum'
        }).reset_index()

        df['percentage'] =  df['totalValue'] / sum(df['totalValue'])
        
        # Fix rounding
        df['totalValue'] = df['totalValue'].round(4)
        df['percentage'] = df['percentage'].round(4)

        return df

    def add_shares(self, file, userid = None):
        df = self.handleCsv(file)
        __share = self.meta.share_info

        df2 = df.loc[:, [ 'isin', 'description', 'market' ]]
        
        df2 = df2.drop_duplicates()
        

        df2.loc[:, 'id'] = [str(_uuid.uuid4()) for _ in range(len(df2.index))]

        with self.db.connect() as conn:
            for row in df2.to_dict(orient='records'):
                stmt = insert(__share).values(row)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['isin', 'market']
                )
                conn.execute(stmt)
            conn.commit()
        
            sel = __share.select().where(__share.c.isin.in_(df['isin'])).where(__share.c.market.in_(df['market']))
            res = conn.execute(sel).fetchall()
        
            if userid != None:
                df3 = pd.merge(df, pd.DataFrame(res), how='left', left_on=['isin', 'market'], right_on=['isin', 'market'])
                df3['share_id'] = df3['id']
                df3['user_id'] = userid
                df3.loc[:, 'id'] = [str(_uuid.uuid4()) for _ in range(len(df3.index))]
                df3 = df3.loc[:, [ 'id', 'share_id', 'order_id', 'user_id', 'count' ]]
                
                for row in df3.to_dict(orient='records'):
                    stmt = insert(self.meta.share_user).values(row)
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=['order_id']
                    )
                    conn.execute(stmt)
                conn.commit()

        return res

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
@app.route('/stocks', methods = ['GET'])
def stocks_groupby(groupby: str = None):
    si = StockImporter()
    
    if groupby == None:
        groupby = ['description', 'ticker']
    
    df = si.get_stocks(request.headers.get('x-userid'), by=groupby)
    
    res = df
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
    res = si.add_shares(f, request.headers.get('x-userid'))
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

@app.route('/import-csv', methods=['POST'])    
def import_csv():
    si = StockImporter()
    f = request.files['file']
    res = si.handleCsv(f)

    return Response(res.to_json(), content_type='application/json')


# Run this on startup
def init():
    si = StockImporter()
    si.meta.meta.create_all(si.db)
    with si.db.connect() as conn:
        conn.execute(sa.sql.text(si.meta.manual_scripts()))
        conn.commit()
    
    
    si.create_account(os.environ.get('OWNER_GUID'))

    
init()
