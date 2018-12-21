import tweepy
import json
import tweepy
import pprint
import pymysql as db
import pandas as pd
import certifi
import ssl
import geopy.geocoders
import matplotlib.pyplot as plt
from config import *
from geopy.geocoders import Nominatim
from gmplot import gmplot
from textblob import TextBlob
from termcolor import colored
from dateutil import parser
from tweepy.api import API
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from tqdm import tqdm

cnxt = db.connect(user='root', password='u0bj8dsvs1n',
                  host='localhost',
                  database='sys',
                  charset='utf8mb4')
cursor = cnxt.cursor()


class MyListener(tweepy.StreamListener):

    def on_connect(self):
        print(colored("Successfully connected to Twitter", "green"))

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print(colored('An error has occured: ', 'red') + repr(status_code))
        return False

    def __init__(self, api=None):
        self.num_tweets = 0
        self.pbar = tqdm(total=100)

    def on_data(self, data):
        try:
            raw_tweets = json.loads(data)
            self.num_tweets += 1
            self.pbar.update(1)
            if 'text' in raw_tweets:
                # Create and process SQL data
                tweet_id = raw_tweets["id"]
                text = raw_tweets["text"]
                created_at = parser.parse(raw_tweets["created_at"])
                screen_name = raw_tweets["user"]["screen_name"]
                location = raw_tweets["user"]["location"]
                query = "INSERT INTO PyData (screen_name, created_at, location, text) VALUES (%s,%s,%s,%s)"
                cursor.execute(
                    query, (screen_name, created_at, location, text))
                cnxt.commit()

        except BaseException as e:
            # Common error: Emoji tweets
            print(colored("Error on_data: %s", "red") % str(e))
        if self.num_tweets < 100:
            return True
        else:
            self.pbar.close()
            cursor.close()
            cnxt.close()
            return False

    def on_error(self, status):
        print(status)
        return True


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def main():
    consumer_key = 'y8js0cEdoYWFT5nQERuEm0fXI'
    consumer_secret = 'DJdiZGtJSODiNQAGSDYhK3Lu4E69xiRHwf6x5nCffUW9Jq7fIm'
    access_token = '32954643-EPgeI3VYUdojmCjZnxQ5XFsBl5EHwhuGYgn4B856p'
    access_secret = 'h0qTDbDK59pGlqtxDuPj6CA3BC6rKr3ewHqLOH4oIEoh4'
    search = input("Company Name: ")
    go = input("Stream? [yn]")
    if (go == "y" or go == 'Y'):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)
        twitter_stream = Stream(auth, MyListener())
        twitter_stream.filter(track=[search])
    elif (go == "n" or go == "N"):
        pass
    main_cnxt = db.connect(user='root', password='u0bj8dsvs1n',
                           host='localhost',
                           database='sys',
                           charset='utf8mb4')
    main_cursor = main_cnxt.cursor()
    main_cursor.execute("SELECT screen_name, location, text FROM PyData ")
    table = main_cursor.fetchall()
    number_rows = main_cursor.execute("SELECT * FROM PyData ")
    main_cnxt.close()
    main_cursor.close()

    # Restruces data into pandas datafram for easy use
    df = pd.DataFrame([[ij for ij in i] for i in table])
    df.rename(columns={0: 'Username', 1: 'Location', 2: 'Text'}, inplace=True)

    # Create init pie chart
    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    num_terms = len(df)
    for i in range(len(df)):
        analysis = TextBlob(df['Text'][i])
        polarity += analysis.sentiment.polarity
        if(analysis.sentiment.polarity > 0.00):
            positive += 1
        elif(analysis.sentiment.polarity < 0.00):
            negative += 1
        elif(analysis.sentiment.polarity == 0):
            neutral += 1
    positive = percentage(positive, num_terms)
    negative = percentage(negative, num_terms)
    neutral = percentage(neutral, num_terms)
    labels = ['Positive [' + str(positive) + '%]', 'Neutral [' + str(neutral) + '%]',
              'Negative [' + str(negative) + '%]']
    sizes = [positive, negative, neutral]
    colors = ['darkgreen', 'gold', 'red']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.title('Sentiment Analysis of Tweets')
    plt.axis('equal')
    plt.tight_layout()
    pie_promt = input("Load pie chart? [yn]")
    if pie_promt == 'y' or pie_promt == 'Y':
        print(colored("Loading pie chart ..", "green"))
        print(colored("Close chart to continue ..", "yellow"))
        plt.show()
    elif(pie_promt == 'n' or pie_promt == 'N'):
        pass

    # Create heat map
    heat_promt = input("Load heat map? [yn]")
    if heat_promt == 'y' or heat_promt == 'Y':
        print(colored("Loading heat map ..", "green"))
        # Bypass for SSL: CERTIFICATE_VERIFY_FAILED
        ctx = ssl.create_default_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx
        geolocator = Nominatim(timeout=10)
        coordinates = {'latitude': [], 'longitude': []}

        for i in range(number_rows):
            location = geolocator.geocode(df["Location"][i])
            if location:
                coordinates['latitude'].append(location.latitude)
                coordinates['longitude'].append(location.longitude)
        gmap = gmplot.GoogleMapPlotter(30, 0, 3)
        gmap.heatmap(coordinates['latitude'],
                     coordinates['longitude'], radius=20)
        gmap.draw("heatmap.html")
    elif(heat_promt == 'n' or heat_promt == 'N'):
        pass
    """
    Note: Getting progress bar for gmap.draw

    with open("gmplot/gmplot.py","r") as f:
        print("n")
        
    """


if __name__ == "__main__":
    main()
