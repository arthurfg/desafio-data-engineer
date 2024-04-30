import os

from time import time

import pandas as pd
from sqlalchemy import create_engine
import json

def ingest_callable(user, password, host, port, db, table_name, json_file):
    print(table_name, json_file)

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()

    print('connection established successfully, inserting data...')

    t_start = time()

    with open(json_file) as file:
        data = json.load(file)    
    # #df_iter = pd.read_csv(json_file, iterator=True, chunksize=100000)
    df = pd.json_normalize(data)
    # # df = next(df_iter)

    # # df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    # # df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

    t_end = time()
    print('inserted the first chunk, took %.3f second' % (t_end - t_start))

    # while True: 
    #     t_start = time()

    #     try:
    #         df = next(df_iter)
    #     except StopIteration:
    #         print("completed")
    #         break

    #     df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)

    #     df.to_sql(name=table_name, con=engine, if_exists='append')

    #     t_end = time()

    #     print('inserted another chunk, took %.3f second' % (t_end - t_start))