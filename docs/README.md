# Motivation
After much brainstorming and soul-searching, we encountered [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset) by [Rounak Banik](https://www.kaggle.com/rounakbanik) on Kaggle, which contained metadata for 45,000 movies listed in the [Full MovieLens Dataset](https://grouplens.org/datasets/movielens/) as well as ratings from 270,000 users for those movies.

The seed of our idea came from the question of how indicative movie trailer YouTube metrics (views, likes, dislikes) would be on movie revenue. We decided to expand that to building a general **movie revenue predictor**, based on various data that would be available before the release of the movie. We had to eventually modify this idea slighty - we will soon explain why.

# Impact
Being able to accurately predict the profitability of a movie could have a massive real world impact. Over the past 5 years, the film industry has generated an average of $10.8 billion in revenue in ticket sales at the box office, and that number gets larger every year. If we count later mechandising and home video sales, that number jumps to $19 billion. As of 2016, the film industry supported 1.9 million U.S. jobs and $121 billion in wages. It is fair to say that it is a significant part of our economy, and predicting the profitability of films is not trivial.

![Hollywood](https://images.pexels.com/photos/164183/pexels-photo-164183.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940 "Hollywood")

# Data curation
A huge amount of the efforts in our project went into curating and cleaning up the dataset. Initially, only 5381 movies out of the 45,000 had the financial data (budget and revenue) we thought would be important. We were also missing certain features we wanted to investigate, like movie trailer metadata from Youtube. We had to find ways to fill in the missing data. Acquiring good data and transforming it into a useful set of features is an extremely important part of Data Science. To help others gain an understanding of how to use public APIs to generate a dataset like we did, the following sections will provide some reference code alongside a description of our motives.

## Filling in movie trailer metadata
Fortunately, the original dataset did provide the TMDb IDs of each of the movies. [The Movie Database](https://www.themoviedb.org/?language=en) (TMDb) is a community-built movie and TV database. Using the TMDb IDs, we could pull the YouTube trailer IDs of the movies using the [TMDb API](https://www.themoviedb.org/documentation/api?language=en). We then used the [YouTube Data API](https://developers.google.com/youtube/v3/getting-started) to pull the trailer views, likes and dislikes for these trailers. 

Here is a helpful function for scraping trailers from TMDb for each ID in our dataset. Please note that TMDb has a 40 request per 10 second interval rate limiting, so be cautious not to upset this.

```
#!/usr/bin/env python
import time
import requests
import pandas as pd

# Specify your TMDb API key
TMDB_API_KEY = ''
TMDB_VIDEO_URL = 'https://api.themoviedb.org/3/movie/{}/videos?api_key={}'

def get_youtube_ids(tmdb_ids):
    trailers = []
    for i in range(len(tmdb_ids)):
        try:
            resp = requests.get(TMDB_VIDEO_URL.format(tmdb_ids[i], TMDB_API_KEY))
            if resp.status_code != 200:
                print('Error: Failed to retrieve video for TMDb ID {} with status code: {}'\
                .format(tmdb_ids[i], resp.status_code))
                trailers.append([])
            else:
                youtube_results = []
                for video in resp.json()['results']:
                    if video['site'] == 'YouTube' and video['type'] in { 'Teaser', 'Trailer' }:
                        youtube_results.append(video['key'])
                trailers.append(youtube_results)
            # Rate limiting, stall 10 seconds
            if i % 40 == 0:
                time.sleep(10)
        except:
            trailers.append([])

    return pd.Series(trailers, index=tmdb_ids)
```

Also, here is a function for querying the YouTube Data API. Please note that YouTube enforces a 1 million request/day quota, so be mindful when scraping for data. There is a lot of data returned by YouTube we are discarding a lot of data besides likes, dislikes, and views. 

```
#!/usr/bin/env python
import requests
import pandas as pd

YOUTUBE_API_KEY = ''
YOUTUBE_DATA_URL = 'https://www.googleapis.com/v3/videos?part=statistics&id={}&key={}'

def get_youtube_metadata(youtube_ids):
    results = {}
    for youtube_id in youtube_ids:
        resp = requests.get(YOUTUBE_DATA_URL.format(youtube_id, YOUTUBE_API_KEY))
        if resp.status_code != 200:
            print('Error: Data retrieval failed for video {} with status code: {}'\
                    .format(youtube_id, resp.status_code))
            results[youtube_id] = {'views':0, 'likes':0, 'dislikes':0}
        else:
            for video_item in youtube_resp.json()['items']:
                try:
                    results[youtube_id] = {\
                        'views': video_item['statistics']['viewCount'], 
                        'likes': video_item['statistics']['likeCount'],
                        'dislikes': video_item['statistics']['dislikeCount']
                    }
                except:
                    print('Error: No statistics available for video {}'.format(youtube_id))  
    return results
```

## Filling in missing financial data
There were still plenty of movies with missing financial data. To try to solve this, we first turned to the [OMDb API](http://www.omdbapi.com/), which was able to give us the revenue values for some rows which had budget but no revenue values. We then turned to the budgets page of [The Numbers](https://www.the-numbers.com/movie/budgets/all/1). Their dataset was difficult to access, so we manually built a web scraper (using [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), a Python library for parsing HTML and XML files) to and extract the budget and revenue data for 5520 movies (as of April 25, 2018). 

From OMDb and The Numbers site, we were able to recover financial data for ~1000 movies. Our final dataset stood at **6234 movies**.

## Feature engineering
There was still plenty of work to be done. A lot of the features available to us in the initial dataset either had to be dropped or modified in order to make them useful.

### One-hot coding of languages, genres
The languages spoken in a movie and the genres which the movie occupied (as determined by the Full MovieLens Dataset) were both available to us as features; however, they were initially available as string representations of Python dictionaries, which made them hard to work with.

![Genres](https://github.com/oupton/startup-ds/blob/master/images/genres.png?raw=true "Genres")

![Languages](https://github.com/oupton/startup-ds/blob/master/images/languages.png?raw=true "Languages")

We decided to extract the data, keep the most frequently seen categories for each, and did a one-hot coding of them so that we could fit a model on them.

### Date features
We also suspected that the date of release would be important; however, just the raw date would be difficult to work with. We thus decided to introduce two features, after some simple parsing: the number of days since the very first movie release date in our dataset (which was February 8, 1915!), and the number of days since the start of the year in which the movie was released.

## Final dataset
After much work, the features we ended up working with were:
- Budget
- Runtime
- YouTube trailer views
- YouTube trailer likes
- YouTube trailer dislikes
- Number of YouTube trailers
- Number of days since first release date
- Number of days since start of that year
- Genres (one-hot coding)
- Number of languages spoken 
- Languages (one-hot coding)

The label we were trying to predict was the **revenue** of each movie.

Now that our dataset was curated, we could get to work building our model.

# Inital attempt

We ran an [XGBoost](http://xgboost.readthedocs.io/en/latest/) Regressor on our data, and found that the mean squared error (MSE) was *~$105M* - comparable to the average movie revenue!

![RMSE](https://github.com/oupton/startup-ds/blob/master/images/xgb_rmse.png?raw=true "RMSE")

We took a second look at our data, and realized that the movie revenue followed a logarithmic distribution, which made it highly imbalanced and thus very hard to predict.

![Revenue](https://github.com/oupton/startup-ds/blob/master/images/revenue_hist.png?raw=true "Revenue")

# The pivot

We thus decided to switch to a binary classification problem of simply **whether a movie would be profitable or not**. We added this feature as boolean variable to the data by simply comparing movie revenue and movie budget, and it turned out that the data was somewhat more balanced.

![Profitability](https://github.com/oupton/startup-ds/blob/master/images/isprofitable.png?raw=true "Profitability")

# Building a model
## Neural nets

We first attempted training [Keras neural nets](https://keras.io/) (KNNs) on our data. We attempted hyperparameter tuning, experimenting with various numbers of hidden layers (between 0 - 2), modes, and functions. However, we could not get it to perform very well - the best area under the curve (AUC) score we could get was *0.5*.

![KNN AUC](https://github.com/oupton/startup-ds/blob/master/images/auc_05.png?raw=true "KNN AUC")

Just flip a coin instead!

## XGBoost

We attempted XGBoost again. Our initial run saw some success, with an AUC score of *~0.75* - already significantly better than the KNNs. We again experimented with hyperparameter tuning, varying the number of estimators (between 50 - 200) and maximum tree depth (between 5 - 15). Our best performance gave us an AUC score of *0.86*, using 50 estimators and with a maximum tree depth of 5.

![XGB AUC](https://github.com/oupton/startup-ds/blob/master/images/auc_086.png?raw=true "XGB AUC") 

# Understanding our model

XGBoost nicely gives us a "Feature Importance" graph of the features used in the model. While the numbers do not directly represent linear coefficients of the features (you can learn about the feature importance function in more detail [here](https://machinelearningmastery.com/feature-importance-and-feature-selection-with-xgboost-in-python/)), they nevertheless give us some insight into which features play a crucial role in determining whether a movie will be profitable or not.

![XGB feature importance](https://github.com/oupton/startup-ds/blob/master/images/xgb_features.png?raw=true "XGB feature importance")

The most important feature was how recently the movie was released, relative to the earliest release date in our data. This makes sense: With technological progress, movie budgets have gone up and filmmakers can depict certain scenes more graphically and realistically. People globally also have more purchasing power, allowing them to spend more on watching movies.

However, it was really interesting that the second-most important feature was which day in the year a movie was released - more so than other factors, including movie budget and genre!

Also, the 3 features we extracted from YouTube data are among the top 7 most important features, which validates our hypothesis that trailer metadata could be predictive of movie profitability.

# Next Steps
## Addressing Potential Problems

One potential problem with our data is that some of the YouTube trailer views and likes may have happened after the movie was released.  If trailers get watched more because movies are successful and not vice versa, this can be a problem.  This would mean feedback or leaking of the Y value into our predictors and reduced usefulness of the algorithm. 

Unfortunately, YouTube does not allow access to historical data about videos (creators can only get access to their own channel history after 2015).  The only way to get this data would be to collect it on new movies before the release.  

We do not think this problem is critical for two reasons.  First, we hypothesize most trailer watches happen before the movie is released since they are released with much fanfare months in advance.  Second, though some of the watch data undoubtedly comes after the release, it is not all caused by the popularity of the movie.  Trailer likes and dislikes will be especially robust to this problem - though popularity may inflate view count, likes and dislikes are based on the quality of the trailer, so it does not matter if they come before or after release date. 

## More Data

As previously mentioned we combined several large movie data sets and the limiting factor was either budget or revenue. We could manually add budget/revenue numbers for movies where our dataset is missing them or try to scrape wikipedia for missing data.  We hypothesize that most of the movies with public revenue or budget numbers have already been added into the datasets.  

## New Features
There are many new features that we hope to find or engineer in our next iteration: 
- view to like ratio
- advertising budget and other budget breakdowns
- actor popularity score
- script metadata
- more movie metadata like location of filming

## More Questions

At some point we would like to return to the original question of movie revenue prediction.  One reason movie revenue was hard to predict is that it is logarithmic.  We could try to predict the log of revenue and see if that helps.

# Credits
- Oliver Upton: [@oupton](https://github.com/oupton)
- Shahid Hussain: [@shahidhn](https://github.com/shahidhn)
- Jacob Read: [@jhr2267](https://github.com/jhr2267)
- Jordan Newman: [@jordanblueman](https://github.com/jordanblueman)