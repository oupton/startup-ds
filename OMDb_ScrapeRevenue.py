#!/usr/bin/env python
import pandas as pd
import requests
import os
import re

url = 'http://www.omdbapi.com/?apikey={}&i={}&plot=full'
api_keys = ['6ba7c3ee','df702266', 'bbc27ce', 'a89c2406']
api_idx = 0
df = pd.read_csv(os.path.join('data', 'missing_financial_data.csv'))
df.budget = df.budget.astype('float64')
budg_only = df[df['budget'] > 0]

revenue = []

for imdb_id in budg_only['recovered_ids']:
    try:
        omdb_resp = requests.get(url.format(api_keys[api_idx], imdb_id))
        if omdb_resp.status_code != 200 or (omdb_resp.json()['Response'] == u'False' and u'IMDb' not in omdb_resp.json()['Error']):
            api_idx += 1
            omdb_resp = requests.get(url.format(api_keys[api_idx], imdb_id))
        revenue.append(re.sub(r'[^0-9]', '', omdb_resp.json()['BoxOffice']) if len(re.sub(r'[^0-9]', '', omdb_resp.json()['BoxOffice'])) != 0 else '0')
    except:
        revenue.append('0')

budg_only['recovered_rev'] = revenue
budg_only[budg_only['recovered_rev'] != '0'].to_csv(os.path.join('data', 'recoved_financial_data.csv'))

