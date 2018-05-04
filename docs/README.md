title: Predicting movie profitability with a data-driven approach

# Motivation
After much brainstorming and soul-searching, we encountered [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset) by [Rounak Banik](https://www.kaggle.com/rounakbanik) on Kaggle, which contained metadata for 45,000 movies listed in the [Full MovieLens Dataset](https://grouplens.org/datasets/movielens/) as well as ratings from 270,000 users for those movies.

The seed of our idea came from the question of how indicative movie trailer YouTube metrics (views, likes, dislikes) would be on movie revenue. We decided to expand that to building a general **movie revenue predictor**, based on various data that would be available before the release of the movie. We had to eventually modify this idea slighty - we will soon explain why.

# Data curation
A huge amount of the efforts in our project went into curating and cleaning up the dataset. Initially, only 5381 movies out of the 45,000 had the financial data (budget and revenue) we thought would be important. We were also missing certain features we wanted to investigate, like movie trailer metadata from Youtube. We had to find ways to fill in the missing data.

## Filling in movie trailer metadata
Fortunately, the original dataset did provide the TMDb IDs of each of the movies. [The Movie Database](https://www.themoviedb.org/?language=en) (TMDb) is a community-built movie and TV database. Using the TMDb IDs, we could pull the YouTube trailer IDs of the movies using the [TMDb API](https://www.themoviedb.org/documentation/api?language=en). We then used the [YouTube Data API](https://developers.google.com/youtube/v3/getting-started) to pull the trailer views, likes and dislikes for these trailers. 

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



# Credits
- Oliver Upton: [@oupton](https://github.com/oupton)
- Shahid Hussain: [@shahidhn](https://github.com/shahidhn)
- Jacob Read: [@jhr2267](https://github.com/jhr2267)
- Jordan Newman: [@jordanblueman](https://github.com/jordanblueman)