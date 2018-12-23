import tweepy
import json
import inquirer
import pymysql as db
import pandas as pd
import certifi
import ssl
import geopy.geocoders
import matplotlib.pyplot as plt
import folium
import time
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
        print(colored('Successfully connected to Twitter', 'green'))

    def __init__(self, api=None):
        self.num_tweets = 0
        self.total_tweets = int(input('Number of tweets:'))
        self.pbar = tqdm(total=self.total_tweets)
        self.unsaved = 0
        self.emojis = 0

    def on_data(self, data):

        try:
            raw_tweets = json.loads(data)
            self.num_tweets += 1
            self.pbar.update(1)
            if 'text' in raw_tweets:
                # Create and process SQL data
                raw_tweets['id']
                text = raw_tweets['text']
                created_at = parser.parse(raw_tweets['created_at'])
                screen_name = raw_tweets['user']['screen_name']
                location = raw_tweets['user']['location']
                query = 'INSERT INTO PyData (screen_name, created_at, location, text) VALUES (%s,%s,%s,%s)'
                cursor.execute(
                    query, (screen_name, created_at, location, text))
                cnxt.commit()
        except BaseException as e:
            # Ignoring emoji tweets for clean output
            if 'Incorrect string value' in str(e):
                self.emojis += 1
                self.unsaved
            else:
                print(colored('Error on_data: %s', 'red') % str(e))
                self.unsaved += 1
        if self.num_tweets < self.total_tweets:
            return True
        else:
            self.pbar.close()
            print(colored('\n' + 'Unsaved Total: ' + str(self.unsaved), 'green'))
            if self.emojis > 0:
                print(colored('Contained Emojis: ' +
                              str(self.emojis) + '\n', 'green'))
            else:
                '\n'
            return False

    def on_error(self, status):
        print('An error has occured: ' + repr(status))
        return True


def process_data():
    main_cnxt = db.connect(user='root', password='u0bj8dsvs1n',
                           host='localhost',
                           database='sys',
                           charset='utf8mb4')
    main_cursor = main_cnxt.cursor()
    main_cursor.execute(
        'SELECT screen_name, location, text FROM PyData ORDER BY created_at DESC')
    table = main_cursor.fetchall()
    number_rows = main_cursor.execute('SELECT * FROM PyData ')
    # Restruces data into pandas datafram for easy use
    processed = pd.DataFrame([[ij for ij in i] for i in table])
    processed.rename(
        columns={0: 'Username', 1: 'Location', 2: 'Text'}, inplace=True)
    return processed, number_rows


def data_size():
    processed = process_data()
    print('Tweets: ' + str(processed[1]))


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def pie_chart(pie_data):
    # Create init pie chart
    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    num_terms = len(pie_data)
    for i in range(len(pie_data)):
        analysis = TextBlob(pie_data['Text'][i])
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
    labels = ['Positive [' + str(positive) + '%]', 'Negative [' + str(negative) + '%]',
              'Neutral [' + str(neutral) + '%]']
    sizes = [positive, negative, neutral]
    colors = ['darkgreen', 'red', 'gold']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc='best')
    plt.title('Sentiment Analysis of Tweets')
    plt.axis('equal')
    plt.tight_layout()
    print(colored('Loading pie chart ..', 'green'))
    print(colored('Close chart to continue ..', 'yellow'))
    # bug: plt crashes on close. Requires 'Quit' option
    plt.show()
    main_menu()


def senti_map(dataframe, count):
    # Create heat map
    print(colored('Loading senti map ..', 'green'))
    # Bypass for SSL: CERTIFICATE_VERIFY_FAILED error
    # import certifi
    # import ssl
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    # replace None in user agent as your email addresss
    # otherwise keep as None
    geolocator = Nominatim(timeout=10, user_agent='Pytweets')
    mapvar = folium.Map(location=[40, -40],
                        zoom_start=3, tiles='Mapbox Control Room')
    for i in range(count):
        location = geolocator.geocode(dataframe['Location'][i])
        if location:
            emotion = TextBlob(dataframe['Text'][i]).sentiment.polarity
            if emotion > 0:
                econ = folium.Icon(color='green')
            elif emotion < 0:
                econ = folium.Icon(color='red')
            elif emotion == 0:
                econ = folium.Icon(color='orange')
            folium.Marker(popup=dataframe['Username'][i] + ': ' + dataframe['Text'][i],
                          location=[location.latitude, location.longitude], icon=econ).add_to(mapvar)
    mapvar.save('sentimap.html')
    print(colored('Click markers for more details', 'green'))
    viz_menu()


def viz_menu():
    viz_data = process_data()
    questions = [
        inquirer.List('Viz_Menu',
                      message='Which visualization do you need?',
                      choices=['Pie Chart', 'Senti Map',
                               'Back', 'Quit'],
                      ),
    ]
    answers = inquirer.prompt(questions)
    if answers['Viz_Menu'] == 'Pie Chart':
        pie_chart(viz_data[0])
    elif answers['Viz_Menu'] == 'Senti Map':
        senti_map(viz_data[0], viz_data[1])
    elif answers['Viz_Menu'] == 'Back':
        if __name__ == '__main__':
            main()
    if answers['Viz_Menu'] == 'Quit':
        return


def main_menu():
    consumer_key = 'y8js0cEdoYWFT5nQERuEm0fXI'
    consumer_secret = 'DJdiZGtJSODiNQAGSDYhK3Lu4E69xiRHwf6x5nCffUW9Jq7fIm'
    access_token = '32954643-EPgeI3VYUdojmCjZnxQ5XFsBl5EHwhuGYgn4B856p'
    access_secret = 'h0qTDbDK59pGlqtxDuPj6CA3BC6rKr3ewHqLOH4oIEoh4'
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    questions = [
        inquirer.List('Main Menu',
                      message='Which operation do you need?',
                      choices=['New Stream', 'Add Terms',
                               'SQL Count', 'Visualization Menu', 'Quit'],), ]
    answers = inquirer.prompt(questions)
    if answers['Main Menu'] == 'New Stream':
        global words
        words = []
        term = input('Search Term: ')
        words.append(term)
        go = input('Stream? [yn]')
        if (go == 'y' or go == 'Y'):
            twitter_stream = Stream(auth, MyListener())
            twitter_stream.filter(track=words)
            main_menu()
        elif (go == 'n' or go == 'N'):
            main_menu()

    elif answers['Main Menu'] == 'Add Terms':
        if 'words' in locals() or 'words' in globals():
            pass
        else:
            words = []
        try:
            while(True):
                add = input('Add Term? [yn]')
                if(add == 'y' or add == 'Y'):
                    new_term = input('New Term: ')
                    words.append(new_term)
                    print('Current List: ', words)
                    go = input('Stream? [yn]')
                    if (go == 'y' or go == 'Y'):
                        twitter_stream = Stream(auth, MyListener())
                        twitter_stream.filter(track=words)
                        main_menu()
                    elif (go == 'n' or go == 'N'):
                        continue
                elif(add == 'n' or add == 'N'):
                    if words:
                        print()
                        print('Current List: ', words)
                        print()
                        return main_menu()
        except BaseException as e:
            print(colored('Error on_data: %s', 'red') % str(e))
            main_menu()

    elif answers['Main Menu'] == 'SQL Count':
        data_size()
        print()
        main_menu()

    elif answers['Main Menu'] == 'Visualization Menu':
        viz_menu()

    elif answers['Main Menu'] == 'Quit':
        return


def main():
    main_menu()


if __name__ == '__main__':
    main()
