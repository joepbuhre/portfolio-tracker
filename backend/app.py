from re import T
from typing import Dict, List
import pandas as pd
import json
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
import os
import requests
import yfinance as yf
from dotenv import load_dotenv

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
        # self.db = sa.create_engine('sqlite:////~/db1.db')
        pass
        
    def getLastQuote(self, ticker: str) -> dict:
        if ticker in dataTickers:
            return dataTickers[ticker]
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

        # Get metadata
        ticks = ' '.join(metadata.values())

        tickers = yf.Tickers(ticks)

        return tickers

    def groupBy(self, colname: str, df: pd.DataFrame) -> pd.DataFrame:
        df2 = df
        
        meta = self.getMetaData([''])

        df2 = df2[df2['Aantal'] > 0]

        if colname not in df.columns:
            def getGrouping(x):
                try:
                    return meta.tickers[x].info[colname]
                except KeyError:
                    return 'Other'
            df2[colname] = df2['Ticker'].apply(lambda x: getGrouping(x))
        
        # Get unique values
        df2 = df2.groupby(
            by=colname
        ).aggregate({
            'currentValue': 'sum',
            'Aantal': 'sum'
        }).reset_index()

        df2['percentage'] =  df2['currentValue'] / sum(df2['currentValue'])

        
        # Fix rounding
        df2['currentValue'] = df2['currentValue'].round(4)
        df2['percentage'] = df2['percentage'].round(4)

        return df2

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
        print(df)

        df = df.groupby(
            by=['Product', 'Ticker']
        ).aggregate({
            'totalValue': 'sum',
            'currentValue': 'sum',
            'Aantal': 'sum'
        }).reset_index()

        # df['GAK'] = df['totalValue'] / df['Aantal']

        return df


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

@app.route('/dataframe/<groupby>', methods = ['GET', 'POST'])
def dataframeGroupBy(groupby: str):
    si = StockImporter()

    if request.method == 'POST':
        f = request.files['file']
        df = si.handleCsv(f)
    else:
        df = si.handleCsv(open('./Transactions.csv'))
        
    # for gr in ['Type', 'Sector', 'Product']:
    #     tst = groupBy(gr, df).to_dict(orient='records')
    res = si.groupBy(groupby, df).to_dict(orient='records')

    return Response(json.dumps(res), content_type='application/json')
