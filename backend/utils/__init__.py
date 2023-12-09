from flask import Response
import datetime
from json import JSONEncoder
from decimal import Decimal
from pandas import Timestamp

class JsonEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime, Timestamp)):
                return obj.isoformat()
            
            if isinstance(obj, (Decimal)):
                 return float(obj)

class Responses:
    def json(obj):
        res = {}
        if type(obj) == str:
             res['message'] = obj
        
        if type(obj) in [dict, list]:
             res = obj
        
        return Response(JsonEncoder().encode(res), content_type='application/json', status=200)
    
    def client_error(string):
         return Response(
              JsonEncoder().encode({
                   'error': string
              }),
              content_type='application/json', status=400
         )
    
    def error(string):
         return Response(
              JsonEncoder().encode({
                   'error': string
              }), 
              content_type='application/json', status=500
         )
    
    def forbidden(string):
         return Response(
              JsonEncoder().encode({
                   'error': 'forbidden'
              }),
              content_type='application/json', status=403
         )