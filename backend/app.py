import pandas as pd
import json
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
import os
import yfinance as yf
from dotenv import load_dotenv
import sqlalchemy as sa
from db_structure.json_encoder import JsonEncoder; 
from db_structure.sql_meta import StockMeta
from stock_importer.StockImporter import StockImporter

load_dotenv()

if 'alphaVantageKey' not in os.environ:
    print('Missing key')
else:
    alphaVantageKey = os.environ['alphaVantageKey']

app = Flask(__name__, static_folder='../frontend/assets',
                        template_folder = "../frontend/")
CORS(app)

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

@app.route('/history', methods = ['GET'])
def get_history():
    tickers = request.args.getlist('ticker')
    tickers.extend(i for i in request.args.getlist('ticker[]') if i not in tickers)

    si = StockImporter()
    hist = si.get_history(tickers)
    return Response(hist, content_type='application/json')

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

# Allow routes only when user is ownerguid
@app.route('/update-stock-prices', methods=['POST'])
def update_stock_prices():
    if(request.headers.get('x-userid') != os.getenv('OWNER_GUID')):
        return Response('Not allowed', status=403)
    
    si = StockImporter()
    res = si.set_prices()
    return Response(JsonEncoder().encode(res), content_type='application/json')


# Run this on startup
def init():
    si = StockImporter()
    si.meta.meta.create_all(si.db)
    with si.db.connect() as conn:
        conn.execute(sa.sql.text(si.meta.manual_scripts()))
        conn.commit()
    
    
    si.create_account(os.environ.get('OWNER_GUID'))
 
init()
