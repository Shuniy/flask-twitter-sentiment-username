# Importing libraries
from flask import Flask, render_template, abort, request
from twython import Twython
import nltk
import sys

# twitter api keys
APP_KEY = 'k9TzaLQPAuKwTBYBvTZOV8yeu'
APP_SECRET = 'EBuHFwCpRFifAfbv2HzpkaJlKP9kVQHr6p8tnHT88m0GO9u3dP'

# using twython to make connection
twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
# obtaining access tokens
ACCESS_TOKEN = twitter.obtain_access_token()

# Creating connection with access tokens
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

# creating app
app = Flask(__name__)

# Creating words dictionary and reading from the txt files


class words_dictionary:
    def __init__(self, file):
        self.list = [line.rstrip('\n') for line in open(file)]
        print("Words in list " + file + ": " + str(len(self.list)))

    def check(self, word):
        if word.lower() in self.list:
            return 1
        else:
            return 0

# creating class for SentimentScore


class SentimentScore:
    def __init__(self, positive_tweets, negative_tweets, neutral_tweets):
        self.positive_tweets = positive_tweets
        self.negative_tweets = negative_tweets
        self.neutral_tweets = neutral_tweets
        self.neg = len(negative_tweets)
        self.pos = len(positive_tweets)
        self.neut = len(neutral_tweets)


dictionaryNegative = words_dictionary('negative-words.txt')

dictionaryPositive = words_dictionary('positive-words.txt')

# function to get sentiment scores


def sentiment(tweet):

    negative_score = 0
    positive_score = 0

    tokenizer = nltk.tokenize.TweetTokenizer()
    tweet_words = tokenizer.tokenize(tweet)

    for word in tweet_words:
        negative_score += dictionaryNegative.check(word)

    for word in tweet_words:
        positive_score += dictionaryPositive.check(word)

    if negative_score > positive_score:
        return 'negative'
    elif negative_score == positive_score:
        return 'neutral'
    else:
        return 'positive'

# using dictionary to count negative frequency


def sentiment_analysis(tweets):

    negative_tweets = []
    positive_tweets = []
    neutral_tweets = []

    for tweet in tweets:
        result = sentiment(tweet['text'])

        if result == 'negative':
            negative_tweets.append(tweet['text'])
        elif result == 'positive':
            positive_tweets.append(tweet['text'])
        else:
            neutral_tweets.append(tweet['text'])
    return SentimentScore(positive_tweets, negative_tweets, neutral_tweets)

# Home
@app.route("/", methods=["POST", "GET"])
def root():
    if request.method == "POST":
        user_timeline = twitter.get_user_timeline(
            screen_name=request.form['twitter_username'], count=100)
        return render_template("result.html", result=sentiment_analysis(user_timeline), username=request.form['twitter_username'])
    else:
        return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
