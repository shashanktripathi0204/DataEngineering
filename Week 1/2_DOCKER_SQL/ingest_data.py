import pandas as pd
from sqlalchemy import create_engine
from time import time

# script created from upload-data.ipynb

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')


df_iter = pd.read_csv('yellow_tripdata_2021-01.csv', iterator=True, chunksize=100000)
df = next(df_iter)
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
df.head(n=0).to_sql(name="yello_taxi_data", con=engine, if_exists='replace')
df.to_sql(name="yello_taxi_data", con=engine, if_exists='append')


while True:
    try:
        t_start = time()
        df = next(df_iter)
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        df.to_sql(name="yello_taxi_data", con=engine, if_exists='append')
        t_end = time()
        
        print("Inserted another chunk..., took %.3f seconds" % (t_end - t_start))
        
    except StopIteration:
        print("All chunks have been processed.")
        break
    except Exception as e:
        print("An error occurred:", e)
        break
# while True:
#     t_start = time()
#     df = next(df_iter)
#     df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
#     df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
#     df.to_sql(name="yello_taxi_data", con=engine, if_exists='append')
#     t_end = time()
    
#     print("Inserted another chunk...., took %.3f second"%(t_end - t_start))



