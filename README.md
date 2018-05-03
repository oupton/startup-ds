# Predicting movie profitability with a data-driven approach

## Motivation
After much brainstorming and soul-searching, we encountered [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset) by [Rounak Banik](https://www.kaggle.com/rounakbanik) on Kaggle, which contained metadata for 45,000 movies listed in the [Full MovieLens Dataset](https://grouplens.org/datasets/movielens/) as well as ratings from 270,000 users for those movies.

The seed of our idea came from the question of how indicative movie trailer YouTube metrics (views, likes, dislikes) would be on movie revenue. We decided to expand that to building a general **movie revenue predictor**, based on various data that would be available before the release of the movie. We had to eventually modify this idea slighty - we will soon explain why.

## Data Curation
The label we were looking at was A huge amount of the efforts in our project went into curating and cleaning up the dataset. Initially, only 5381 movies out of the 45,000 had the financial data (budget and revenue) we thought would be important. We were also missing certain features we wanted to investigate, like movie trailer metadata from Youtube. We had to find ways to fill in the missing data.

### Filling in movie trailer metadata
Fortunately, the original dataset did provide the TMDb IDs of each of the movies. [The Movie Database](https://www.themoviedb.org/?language=en) (TMDb) is a community-built movie and TV database. Using the TMDb IDs, we could pull the YouTube trailer IDs of the movies using the [TMDb API](https://www.themoviedb.org/documentation/api?language=en). We then used the [YouTube Data API](https://developers.google.com/youtube/v3/getting-started) to pull the trailer views, likes and dislikes for these trailers. 

### Filling in missing financial data
There were still plenty of movies with missing financial data. To try to solve this, we first turned to the [OMDb API](http://www.omdbapi.com/), which was able to give us the revenue values for some rows which had budget but no revenue values. We then turned to the budgets page of [The Numbers](https://www.the-numbers.com/movie/budgets/all/1). Their dataset was difficult to access, so we manually built a web scraper (using [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), a Python library for parsing HTML and XML files) to and extract the budget and revenue data for 5520 movies (as of April 25, 2018). 

From OMDb and The Numbers site, we were able to recover financial data for ~1000 movies. Our final dataset stood at **6234 movies**.

### Feature engineering
There was still plenty of work to be done. A lot of the features available to us in the initial dataset either had to be dropped or modified in order to make them useful.

#### One-hot coding of languages, genres
The languages spoken in a movie and the genres which the movie occupied (as determined by the Full MovieLens Dataset) were both available to us as features; however, they were initially available as string representations of Python dictionaries, which made them hard to work with.



## Credits
- Oliver Upton: [@oupton](https://github.com/oupton)
- Shahid Hussain: [@shahidhn](https://github.com/shahidhn)
- Jacob Read: [@jhr2267](https://github.com/jhr2267)
- Jordan Newman: [@jordanblueman](https://github.com/jordanblueman)