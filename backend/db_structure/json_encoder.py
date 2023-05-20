import datetime
from json import JSONEncoder
from decimal import Decimal

class JsonEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            
            if isinstance(obj, (Decimal)):
                 return float(obj)