from datetime import date
import datetime
import pandas as pd
from pyxirr import xirr

dates = [date(2020, 1, 1), date(2021, 1, 1), date(2022, 1, 1)]
amounts = [-1000, 750, 500]

data = [{"purchase_date":"2023-11-17","mutation":0.7200}, 
 {"purchase_date":"2023-11-17","mutation":-0.1100}, 
 {"purchase_date":"2023-09-28","mutation":2.1400}, 
 {"purchase_date":"2023-09-14","mutation":4.4000}, 
 {"purchase_date":"2023-09-14","mutation":-0.6600}, 
 {"purchase_date":"2023-09-13","mutation":6.2000}, 
 {"purchase_date":"2023-09-13","mutation":-0.9300}, 
 {"purchase_date":"2023-08-25","mutation":302.4000}, 
 {"purchase_date":"2023-08-25","mutation":-280.9600}, 
 {"purchase_date":"2023-08-25","mutation":-2.0000}, 
 {"purchase_date":"2023-08-25","mutation":-302.4000}, 
 {"purchase_date":"2023-08-18","mutation":0.7200}, 
 {"purchase_date":"2023-08-18","mutation":-0.1100}, 
 {"purchase_date":"2023-08-15","mutation":3.8500}, 
 {"purchase_date":"2023-08-15","mutation":-0.5800}, 
 {"purchase_date":"2023-07-20","mutation":-1.0000}, 
 {"purchase_date":"2023-07-20","mutation":-231.3600}, 
 {"purchase_date":"2023-07-20","mutation":-1.0000}, 
 {"purchase_date":"2023-07-20","mutation":-103.1400}, 
 {"purchase_date":"2023-06-29","mutation":1.3700}, 
 {"purchase_date":"2023-06-15","mutation":7.6000}, 
 {"purchase_date":"2023-06-15","mutation":-1.1400}, 
 {"purchase_date":"2023-06-02","mutation":543.0000}, 
 {"purchase_date":"2023-06-02","mutation":-505.5400}, 
 {"purchase_date":"2023-06-02","mutation":-2.0000}, 
 {"purchase_date":"2023-06-02","mutation":-543.0000}, 
 {"purchase_date":"2023-05-26","mutation":467.2000}, 
 {"purchase_date":"2023-05-26","mutation":-436.4700}, 
 {"purchase_date":"2023-05-26","mutation":-2.0000}, 
 {"purchase_date":"2023-05-26","mutation":-467.2000}, 
 {"purchase_date":"2023-05-22","mutation":322.8000}, 
 {"purchase_date":"2023-05-22","mutation":-299.2200}, 
 {"purchase_date":"2023-05-22","mutation":-2.0000}, 
 {"purchase_date":"2023-05-22","mutation":-322.8000}, 
 {"purchase_date":"2023-05-22","mutation":-344.1000}, 
 {"purchase_date":"2023-05-08","mutation":-0.6400}, 
 {"purchase_date":"2023-05-22","mutation":317.4600}, 
 {"purchase_date":"2023-05-22","mutation":-2.0000}, 
 {"purchase_date":"2023-05-22","mutation":344.1000}, 
 {"purchase_date":"2023-05-18","mutation":313.8000}, 
 {"purchase_date":"2023-05-18","mutation":-291.6300}, 
 {"purchase_date":"2023-05-18","mutation":-2.0000}, 
 {"purchase_date":"2023-05-18","mutation":-313.8000}, 
 {"purchase_date":"2023-05-17","mutation":-273.0600}, 
 {"purchase_date":"2023-05-17","mutation":251.2700}, 
 {"purchase_date":"2023-05-17","mutation":-2.0000}, 
 {"purchase_date":"2023-05-17","mutation":273.0600}, 
 {"purchase_date":"2023-05-17","mutation":270.7200}, 
 {"purchase_date":"2023-05-17","mutation":-250.6200}, 
 {"purchase_date":"2023-05-17","mutation":-2.0000}, 
 {"purchase_date":"2023-05-17","mutation":-270.7200}, 
 {"purchase_date":"2023-05-08","mutation":4.2800}, 
 {"purchase_date":"2023-05-03","mutation":0.1500}, 
 {"purchase_date":"2023-05-02","mutation":-0.1900}, 
 {"purchase_date":"2023-05-02","mutation":-4.9000}, 
 {"purchase_date":"2023-05-02","mutation":-188.0000}, 
 {"purchase_date":"2023-05-02","mutation":-3.9000}, 
 {"purchase_date":"2023-05-02","mutation":150.3200}, 
 {"purchase_date":"2023-05-02","mutation":-0.1500}, 
 {"purchase_date":"2023-05-02","mutation":-3.9000}, 
 {"purchase_date":"2023-05-02","mutation":-148.4000}, 
 {"purchase_date":"2023-04-21","mutation":-3.0000}, 
 {"purchase_date":"2023-04-21","mutation":-128.6300}, 
 {"purchase_date":"2023-04-21","mutation":-3.0000}, 
 {"purchase_date":"2023-04-21","mutation":-146.3000}, 
 {"purchase_date":"2023-04-03","mutation":-206.8200}, 
 {"purchase_date":"2023-04-03","mutation":-143.3200}, 
 {"purchase_date":"2023-03-30","mutation":0.8600}, 
 {"purchase_date":"2023-03-02","mutation":-70.9900}, 
 {"purchase_date":"2023-03-02","mutation":-210.7000}, 
 {"purchase_date":"2023-12-05","mutation":3355.33960000}]

res = xirr(
        zip(
            list(map(lambda x: datetime.datetime.strptime(x['purchase_date'], "%Y-%m-%d").date(), data)),
            list(map(lambda x: x['mutation'], data))
        )
    )
print(res)

# print (
#     pd.DataFrame(dates,amounts).to_csv('./test2.csv')
# )