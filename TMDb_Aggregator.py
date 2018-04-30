#!/usr/bin/env python
import requests
import pandas as pd
import os
import time

class Aggregator:

    def __init__(self, api_key):
        self.movie_url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'
        self.video_url = 'https://api.themoviedb.org/3/movie/{}/videos?api_key={}'
        self.tmdb_api_key = api_key

    def __query_tmdb(self, tmdb_id):
        videos_resp = requests.get(self.video_url.format(tmdb_id, self.tmdb_api_key))

        if videos_resp.status_code != 200:
            print('Error: Couldn\'t load videos for movie with TMDB ID: {}'.format(tmdb_id))
            return []

        retVal = []

        for video in videos_resp.json()['results']:
            if video['site']  == u'YouTube' and (video['type'] == u'Teaser' or video['type'] == u'Trailer'):
                retVal.append(video['key']) 
        
        return retVal

    def test_query_tmdb(self, tmdb_id):
        return self.__query_tmdb(str(int(tmdb_id)))

    

if __name__ == '__main__':
    agg = Aggregator('4cb0c9b9398836f9fad813287e3cbfba')
    movies_df = pd.read_csv(os.path.join('data', 'links.csv'))
    idx = 0
    videos_col = []
    for tmdb_id in movies_df['tmdbId']:
        idx += 1
        videos_col.append(agg.test_query_tmdb(tmdb_id))
        if idx % 40 == 0:
            time.sleep(11)

    movies_df['trailers'] = videos_col
    movies_df.to_csv(os.path.join('data', 'videos.csv'))