from datetime import datetime as dt, timedelta as td
import time
import pandas as pd
import json
from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
import os
import yfinance as yf
from dotenv import load_dotenv
import sqlalchemy as sa
from app_manager.app_manager import AppManager
from stock_manager.degiro import DeGiro
from utils import Responses
from utils.exceptions import NotExistException
from db_structure.json_encoder import JsonEncoder; 
from db_structure.sql_meta import StockMeta
from stock_importer.StockImporter import StockImporter
from sqlalchemy.dialects import postgresql as pg

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
def stocks_groupby(groupby: str = None):
    tm = time.perf_counter()
    print(f'Started at {tm}')
    
    si = StockImporter()
    
    if groupby == None:
        groupby = ['description', 'ticker']
    else:
        groupby = groupby.split('-')
    
    df = si.get_stocks(request.headers.get('x-userid'), by=groupby)

    print(f'Function took: {time.perf_counter() - tm}')
    res = df
    return Response(res.to_json(orient='records'), content_type='application/json')

@app.route('/history', methods = ['GET'])
def get_history():
    si = StockImporter()
    am = AppManager()
    tickers = request.args.getlist('ticker')
    tickers.extend(i for i in request.args.getlist('ticker[]') if i not in tickers)

    userid = request.headers.get('x-userid')


    if len(tickers) == 0 and userid == None:
        return Response(json.dumps({'error': 'Userid and / or tickers in query params missing'}), status=400, content_type='application/json')
    elif len(tickers) == 0 and am.login(userid) == True:
        hist = si.get_history(userid=userid)
    elif len(tickers) > 0:
        hist = si.get_history(tickers)
    else:
        return Response(json.dumps({'error': 'Unhandled error. Please check your request'}), status=400, content_type='application/json')
        


    return Response(JsonEncoder().encode(hist), content_type='application/json')

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
    am = AppManager()

    if am.login(request.headers.get('x-userid')) == False:
        return Responses.forbidden()

        
    f = request.files['file']
    res = si.add_shares(f, request.headers.get('x-userid'))
    return Responses.json(res)

@app.route('/create-account', methods=['POST'])
def create_account():
    am = AppManager()
    guid = am.create_account()

    return Responses.json({
        'uuid': guid[0]
    })

@app.route('/login', methods=['POST'])
def check_auth():
    am = AppManager()
    res = am.login(request.headers.get('x-userid'))
    if res:
        return Responses.json({
            'success': res
        })
    else:
        return Responses.forbidden()

@app.route('/import-csv', methods=['POST'])    
def import_csv():
    si = StockImporter()
    f = request.files['file']
    res = si.handleCsvAccount(f)

    return Responses.json(res.to_dict(orient='records'))


# Allow routes only when user is ownerguid
@app.route('/update-stock-prices', methods=['POST'])
def update_stock_prices():
    if(request.headers.get('x-userid') != os.getenv('OWNER_GUID')):
        return Response('Not allowed', status=403)
    
    si = StockImporter()
    res = si.set_prices()
    return Response(JsonEncoder().encode(res), content_type='application/json')

@app.route('/set-stock-history', methods=['POST'])
def set_stock_history():
    if(request.headers.get('x-userid') != os.getenv('OWNER_GUID')):
        return Response('Not allowed', status=403)
    
    if 'ticker' not in request.json:
        return Responses.error('Missing required param "ticker"') 
    try:
        body = request.json['filter'] if 'filter' in request.json else None
        res = StockImporter().set_history(**request.json)
        return Responses.json(res)
    except NotExistException as e:
        return Responses.client_error(e.msg)
    except Exception as e:
        print(e)
        return Responses.error('unkown error occured')

@app.route('/reset-database', methods=['GET', 'POST'])
def reset_database():
    if(request.headers.get('x-userid') != os.getenv('OWNER_GUID')):
        return Response('Not allowed', status=403)
    
    # If GET > return auth token
    si = StockImporter()
    from base64 import b64decode, b64encode
    from secrets import token_urlsafe

    if request.method == 'GET':
        # JWT
        dic = {'token': token_urlsafe(50), 'expires': dt.isoformat(dt.now() + td(minutes=15))}
        token = (b64encode(json.dumps(dic).encode('utf-8'))).decode('utf-8')

        with si.db.connect() as conn:
            # stm = si.meta.config.insert()
            stmt = pg.insert(si.meta.config).values({'key': 'reset_token', 'value': token})
            stmt = stmt.on_conflict_do_update(
                constraint=si.meta.config.primary_key, 
                set_={'key': 'reset_token', 'value': token}

            )
            conn.execute(stmt)
            conn.commit()

        return Response(json.dumps({'token': token, 'message': 'please backup important data when resetting db'}), content_type='application/json')
    
    if request.method == 'POST':
        with si.db.connect() as conn:
            stmt = sa.sql.select(si.meta.config.c.value).where(si.meta.config.c.key == 'reset_token') 
            res = conn.execute(stmt).fetchone()
        
            if res == None:
                return Response('unauthorized', status=403)

            saved_token = json.loads((b64decode(res[0])).decode('utf-8'))
            if dt.strptime(saved_token['expires'], '%Y-%m-%dT%H:%M:%S.%f') < dt.now():
                return Response('token has expired', status=401)
            
            else:
                for tbl in si.meta.meta.tables:
                    conn.execute(sa.sql.text(f'drop table "{tbl}";'))
                
                conn.commit()
                
                return Response('Resetted Database')

@app.route('/stocks', methods = ['GET'])
def stock():
    if(request.headers.get('x-userid') != os.getenv('OWNER_GUID')):
        return Response('Not allowed', status=403)
    
    si = StockImporter()
    res = si.get_share_info(user_id=request.headers.get('x-userid'),by=['isin', 'ticker', 'share_id'])

    return Response(json.dumps(res), content_type='application/json')

@app.route('/stock-actions',methods=['GET'])
def get_actions():
    dg = DeGiro()
    return Responses.json(
        dg.get_account()
    )


@app.route('/match-ticker', methods = ['POST'])
def match_ticker():
    data = request.get_json(force=True)
    si = StockImporter()
    si.match_ticker(data)

    return Response('OK')

# Run this on startup
def init():
    am = AppManager()
    am.meta.meta.create_all(am.db)
    with am.db.connect() as conn:
        conn.execute(sa.sql.text(am.meta.manual_scripts()))
        conn.commit()
    
    
    am.create_account(os.environ.get('OWNER_GUID'))
 
