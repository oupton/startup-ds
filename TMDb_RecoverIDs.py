#!/usr/bin/env python
import pandas as pd
import requests
from joblib import Parallel, delayed
import os
import threading
import time

lock = threading.Lock()
count = 0
url = 'https://api.themoviedb.org/3/movie/{}?api_key=4cb0c9b9398836f9fad813287e3cbfba'

df = pd.read_csv(os.path.join('data', 'missing_financial_data.csv'))

def get_IMDb_Id(tmdb_id):
    global count
    lock.acquire()
    count += 1
    if count % 8 == 0:
        time.sleep(10)
    lock.release()
    tmdb_resp = requests.get(url.format(tmdb_id))
    if tmdb_resp.status_code != 200:
        print('Couldn\'t retrieve TMDb ID: {}'.format(tmdb_id))
        return '-1'
    try:
        id = tmdb_resp.json()['imdb_id']
        print('Recovered id IMDb ID: {} for TMDb ID: {}'.format(id, tmdb_id))
    except:
        return '-1'

df['recovered_ids'] = Parallel(n_jobs=4)(delayed(get_IMDb_Id)(tmdb_id) for tmdb_id in df['id'].astype('int').astype('str'))