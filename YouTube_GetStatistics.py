#!/usr/bin/env python
import os
import time
import pandas as pd
import requests

url = 'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={}&key={}'
api_key = 'AIzaSyBNJ7iTaawZD2_rqDIH7UOUJPF7N5x2rb0'

videos_df = pd.read_csv(os.path.join('data', 'videos.csv'))
views = []
likes = []
dislikes = []

i = 0
for trailer_set in videos_df['trailers']:
    viewsCount, likesCount, dislikesCount = 0, 0, 0
    trailer_set = trailer_set.replace('u\'', '').replace('\'', '').replace('[', '').replace(']','').split(',')

    for trailer in trailer_set:
        i += 1
        if trailer == '':
            continue

        youtube_resp = requests.get(url.format(trailer.strip(), api_key))
        if youtube_resp.status_code != 200:
            print('API Error: Couldn\'t retrieve stats for id: {}'.format(trailer))
            continue

        for video_entity in youtube_resp.json()['items']:
            try:
                viewsCount += int(video_entity['statistics']['viewCount'])
                likesCount += int(video_entity['statistics']['likeCount'])
                dislikesCount += int(video_entity['statistics']['dislikeCount'])
            except:
                continue

        if i % 1000 == 0:
            print('Digested {} YouTube videos'.format(i))

    views.append(viewsCount)
    likes.append(likesCount)
    dislikes.append(dislikesCount)

videos_df['views'] = views
videos_df['likes'] = likes
videos_df['dislikes'] = dislikes
videos_df.to_csv(os.path.join('data', 'video_metadata.csv'))

