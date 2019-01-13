import os
import sys
import ssl
import json
import tweepy
import certifi
import inquirer
import pymysql as db
import pandas as pd
import geopy.geocoders
import matplotlib.pyplot as plt
import folium
import seaborn as sns
from tweepy.streaming import StreamListener
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.api import API
from dateutil import parser
from termcolor import colored
from textblob import TextBlob
from geopy.geocoders import Nominatim
from config import *
from folium.plugins import MarkerCluster
from tqdm import tqdm


class MyListener(tweepy.StreamListener):

    """
    MyListerner collects and manages incoming data using Tweepy.
    Here script.py access Tweepy's library to perform conective duties
    with Twitter's API.
    """

    def on_connect(self):
        """
        Notifies user that Tweepy successfully connected to Twitterself.
        """

        print(colored("Successfully connected to Twitter", "green"))

    def __init__(self, api=None):
        """
        Sets and organizes defult values for variables exclusive to the
        MyListerner class.
        """

        self.num_tweets = 0
        self.total_tweets = int(input("Number of tweets:"))
        self.pbar = tqdm(total=self.total_tweets)
        self.unsaved = 0
        self.emojis = 0

    def on_data(self, data):
        """
        Here data is streamed, parsed into a JSON format, and then
        delivered to MySQL for later use. Any errors in data will be
        reported to the terminal.
        """

        try:
            portal_1 = creds()
            rawTweets = json.loads(data)
            self.num_tweets += 1
            self.pbar.update(1)
            if "text" in rawTweets:
                # Create and process SQL data
                text = rawTweets["text"]
                created_at = parser.parse(rawTweets["created_at"])
                screen_name = rawTweets["user"]["screen_name"]
                location = rawTweets["user"]["location"]
                followers_count = rawTweets["user"]["followers_count"]
                query = "INSERT INTO PyData (screen_name, created_at,\
                    location, followers_count, text) VALUES (%s,%s,%s,%s,%s)"
                portal_1[1].execute(
                    query,
                    (screen_name, created_at, location, followers_count, text))
                portal_1[0].commit()
        except BaseException as e:
            # Ignoring emoji tweets for clean output
            if "Incorrect string value" in str(e):
                self.emojis += 1
                self.unsaved += 1
            else:
                print(colored("Error on_data: %s", "red") % str(e))
                self.unsaved += 1
        if self.num_tweets < self.total_tweets:
            return True
        else:
            self.pbar.close()
            print(colored("\n" + "Unsaved Total: " + str(self.unsaved), "green"))
            if self.emojis > 0:
                print(colored("Contained Emojis: " +
                              str(self.emojis) + "\n", "green"))
            else:
                "\n"
            return False

    def on_error(self, status):
        """
        Reports any errors on Tweepy's connection
        """

        print("An error has occured: " + repr(status))
        return True


def creds():
    """
    Connects the user to MySQl and opens a new cursor
    """

    cnxt = db.connect(user="root", password="u0bj8dsvs1n",
                      host="localhost",
                      database="sys",
                      charset="utf8mb4")
    cursor = cnxt.cursor()
    return cnxt, cursor


def delete_data():
    """
    This function clears MySQL of all data. Usefull for testing
    results in Sentimap().
    """

    ask = input("Reset PyData? [yn]")
    if ask == "y" or ask == "Y":
        try:
            portal_2 = creds()
            cursor = portal_2[0].cursor()
            delete = "truncate PyData"
            cursor.execute(delete)
            remainder = cursor.execute("SELECT * FROM PyData ")
            print(colored("Remaining rows: " + str(remainder), "green"))
        except BaseException as e:
            print(colored("Error on_data: %s", "red") % str(e))
    elif ask == "n" or ask == "N":
        main_menu()


def process_data():
    """
    Creates the main dataframe using the selected JSON categories
    """

    portal_3 = creds()
    cursor = portal_3[0].cursor()
    cursor.execute(
        "SELECT screen_name, created_at, location, followers_count, \
            text FROM PyData ORDER BY created_at DESC")
    rows = cursor.fetchall()
    # Restruces data into pandas datafram for easy use
    processed = pd.DataFrame([[ij for ij in i] for i in rows])
    processed.rename(columns={0: "Username", 1: "Created at",
                              2: "Location", 3: "Followers",
                              4: "Text"}, inplace=True)
    return processed


def data_size():
    """
    Prints out the number of rows in MySQL
    """

    processed = process_data()
    print("Tweets: " + str(len(processed)))


def percentage(part, whole):
    """
    Calculates the percentage of sentiments in
    data set
    """

    return 100 * float(part) / float(whole)


def pie_chart(pie_data):
    """
    Creates a pie chart using the percentages per sentiment type
    """

    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    pie_count = len(pie_data)
    for i in range(pie_count):
        analysis = TextBlob(pie_data["Text"][i])
        polarity += analysis.sentiment.polarity
        if(analysis.sentiment.polarity > 0.00):
            positive += 1
        elif(analysis.sentiment.polarity < 0.00):
            negative += 1
        elif(analysis.sentiment.polarity == 0):
            neutral += 1
    positive = percentage(positive, pie_count)
    negative = percentage(negative, pie_count)
    neutral = percentage(neutral, pie_count)
    labels = ["Positive [" + str(round(positive)) + "%]",
              "Negative [" + str(round(negative)) + "%]",
              "Neutral [" + str(round(neutral)) + "%]"]
    sizes = [positive, negative, neutral]
    colors = ["darkgreen", "red", "gold"]
    patches = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.title("Sentiment Analysis of Tweets")
    plt.axis("equal")
    plt.tight_layout()
    print(colored("Loading pie chart ..", "green"))
    print(colored("Close chart to continue ..", "yellow"))
    # bug: plt crashes on close / fix: restart script
    plt.show()
    os.execl(sys.executable, os.path.abspath("script.py"), *sys.argv)


def heat_map(heat_data):
    """
    This function creates a heatmap. The data visualization shown,
    presents the average polarity within each group. The y-axis contains
    the number of users that fall within the inclusive followers range.
    The x-axis contains the number of followers that fall within the inclusive
    polarity range. (May be replaced soon)
    """

    pol_list, fol_list, fol_count_list, pol_count_list, pol_tots = \
        [], [], [], [], []
    pol_tot_1, pol_tot_2, pol_tot_3, pol_tot_4, pol_tot_5 = 0, 0, 0, 0, 0
    fol_count_1, fol_count_2, fol_count_3 = 0, 0, 0
    fol_count_4, fol_count_5 = 0, 0
    pol_count_1, pol_count_2, pol_count_3 = 0, 0, 0
    pol_count_4, pol_count_5 = 0, 0
    for i in range(len(heat_data)):
        polarity = TextBlob(heat_data["Text"][i]).sentiment.polarity
        followers = heat_data["Followers"][i]
        # create list of polarities and followers from each user
        pol_list.append(polarity)
        fol_list.append(followers)
    for i in range(len(heat_data)):
        # update Follower counts
        # save polarities in each follower group for later averaging
        if fol_list[i] < 10**1 and fol_list[i] >= 0:
            fol_count_1 += 1
            pol_tot_1 += round(TextBlob(heat_data["Text"]
                                        [i]).sentiment.polarity, 2)

        elif fol_list[i] < 10**2 and fol_list[i] >= 10**1:
            fol_count_2 += 1
            pol_tot_2 += round(TextBlob(heat_data["Text"]
                                        [i]).sentiment.polarity, 2)

        elif fol_list[i] < 10**3 and fol_list[i] >= 10**2:
            fol_count_3 += 1
            pol_tot_3 += round(TextBlob(heat_data["Text"]
                                        [i]).sentiment.polarity, 2)

        elif fol_list[i] < 10**4 and fol_list[i] >= 10**3:
            fol_count_4 += 1
            pol_tot_4 += round(TextBlob(heat_data["Text"]
                                        [i]).sentiment.polarity, 2)

        elif fol_list[i] >= 10**4:
            fol_count_5 += 1
            pol_tot_5 += round(TextBlob(heat_data["Text"]
                                        [i]).sentiment.polarity, 2)

        # update Polarity counts
        if pol_list[i] < -1.6:
            pol_count_1 += 1

        elif pol_list[i] > -1.6 and pol_list[i] < -0.6:
            pol_count_2 += 1

        elif pol_list[i] > -0.6 and pol_list[i] < 0.6:
            pol_count_3 += 1

        elif pol_list[i] > 0.6 and pol_list[i] < 1.6:
            pol_count_4 += 1

        else:
            pol_count_5 += 1
    # create y axis data containing count of followers in specific interval
    fol_count_list.extend(
        [fol_count_1, fol_count_2, fol_count_3, fol_count_4, fol_count_5])
    # create x axis data containing count of polarities in specific interval
    pol_count_list.extend(
        [pol_count_1, pol_count_2, pol_count_3, pol_count_4, pol_count_5])
    pol_tots.extend([round(pol_tot_1, 2), round(pol_tot_2, 2), round(
        pol_tot_3, 2), round(pol_tot_4, 2), round(pol_tot_5, 2)])
    r1, r2, r3, r4, r5 = [], [], [], [], []
    rows = [r1, r2, r3, r4, r5]
    # create each row with calculated averages
    for i in range(len(rows)):
        for j in pol_count_list:
            if j == 0:
                rows[i].append(0.0)
            else:
                rows[i].append(round((pol_tots[i] / j), 3))

    df = pd.DataFrame(rows, fol_count_list, pol_count_list)
    sns.heatmap(df, annot=True, fmt="g", cmap='viridis')
    plt.title("Average Sentiment Polarity by Group")
    plt.ylabel("hello")
    plt.ylabel('10,000     10,000     1,000     100     10')
    plt.xlabel(
        '-2.0            -1.0             0.0             1.0             2.0')
    plt.show()


def senti_map(senti_data):
    """
    This function creates a map containing all tweets from
    the users database. Each marker on the map points to the
    the locations from where the tweet was created. Also, each
    marker receives the username, tweet, timestamp, and color
    corresponding to the tweet's sentiment value.
    """

    portal_4 = creds()
    cursor = portal_4[0].cursor()
    count = cursor.execute("SELECT * FROM PyData ")
    # Create heat map
    print(colored("Loading senti map ..", "green"))
    # Bypass for SSL: CERTIFICATE_VERIFY_FAILED error
    # import certifi
    # import ssl
    try:
        ctx = ssl.create_default_context(cafile=certifi.where())
        geopy.geocoders.options.default_ssl_context = ctx
        # replace None in user agent as your email addresss
        # otherwise keep as None
        geolocator = Nominatim(timeout=100, user_agent="Pytweets")
        mapvar = folium.Map(location=[40, -40],

                            zoom_start=3, tiles="Mapbox Control Room")
        cords = 0
        sentibar = tqdm(total=count)
        cluster = folium.plugins.MarkerCluster().add_to(mapvar)
        for i in range(count):
            location = geolocator.geocode(senti_data["Location"][i])
            if location:
                polarity = TextBlob(senti_data["Text"][i]).sentiment.polarity
                if polarity > 0.0:
                    econ = folium.Icon(color="green")
                elif polarity < 0.0:
                    econ = folium.Icon(color="red")
                elif polarity == 0.0:
                    econ = folium.Icon(color="orange")
                folium.Marker(popup="@" + senti_data["Username"][i] + ": " + senti_data["Text"][i] +
                              " Followers: "
                              + str(senti_data["Followers"][i])
                              + " Created at: "
                              + str(senti_data["Created at"][i]),
                              location=[location.latitude, location.longitude], icon=econ).add_to(cluster)
            cords += 1
            sentibar.update(1)
        sentibar.close()
        mapvar.save("sentimap.html")
        print(colored("Click markers for more details", "green"))
        v_menu()
    except BaseException as e:
        print(colored("Geocode Error: %s", "red") % str(e))


def v_menu():
    """
    Generates a menu of available data visualizations
    """

    v_data = process_data()
    questions = [
        inquirer.List("visuals",
                      message="Which visualization do you need?",
                      choices=["Pie Chart", "Senti Map", "Heat Map",
                               "Back", "Quit"],
                      ),
    ]
    answers = inquirer.prompt(questions)
    if answers["visuals"] == "Pie Chart":
        pie_chart(v_data)
    elif answers["visuals"] == "Senti Map":
        senti_map(v_data)
    elif answers["visuals"] == "Heat Map":
        heat_map(v_data)
    elif answers["visuals"] == "Back":
        if __name__ == "__main__":
            main()
    elif answers["visuals"] == "Quit":
        sys.exit()


def main_menu():
    """
    Authorizes the use of Twitter's API and allows
    the user to call main functions from a menu format
    """

    consumerKey = "y8js0cEdoYWFT5nQERuEm0fXI"
    consumerSecret = "DJdiZGtJSODiNQAGSDYhK3Lu4E69xiRHwf6x5nCffUW9Jq7fIm"
    accessToken = "32954643-EPgeI3VYUdojmCjZnxQ5XFsBl5EHwhuGYgn4B856p"
    accessSecret = "h0qTDbDK59pGlqtxDuPj6CA3BC6rKr3ewHqLOH4oIEoh4"
    auth = OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessSecret)
    questions = [
        inquirer.List("Main Menu",
                      message="Which operation do you need?",
                      choices=["New Stream", "Add Terms", "Stream", "Get Words",
                               "SQL Count", "SQL Reset", "Visualization Menu", "Quit"],), ]
    answers = inquirer.prompt(questions)

    global WORDS
    if answers["Main Menu"] == "New Stream":
        WORDS = []
        term = input("Search Term: ")
        WORDS.append(term)
        print("Current List: ", WORDS)
        a = input("Stream? [yn]")
        if a == "y" or a == "Y":
            twitter_stream = Stream(auth, MyListener())
            twitter_stream.filter(languages=["en"], track=WORDS)
            main_menu()
        elif a == "n" or a == "N":
            main_menu()

    elif answers["Main Menu"] == "Add Terms":
        if "WORDS" in locals() or "WORDS" in globals():
            pass
        else:
            WORDS = []
        while True:
            new_term = input("New Term: ")
            WORDS.append(new_term)
            print("Current List: ", WORDS)
            b = input("Stream? [yn]")
            if b == "y" or b == "Y":
                twitter_stream = Stream(auth, MyListener())
                twitter_stream.filter(track=WORDS)
                main_menu()
            elif b == "n" or b == "N":
                print()
                print("Current List: ", WORDS)
                print()
                main_menu()
    elif answers["Main Menu"] == "Stream":
        try:
            c = input("Stream? [yn]")
            if c == "y" or c == "Y":
                twitter_stream = Stream(auth, MyListener())
                twitter_stream.filter(track=WORDS)
                main_menu()
            elif c == "n" or c == "N":
                print()
                print("Current List: ", WORDS)
                print()
                main_menu()
        except BaseException as e:
            print(colored("Error: %s", "red") % str(e))
            main_menu()

    elif answers["Main Menu"] == "Get Words":
        try:
            print()
            print("Current List: ", WORDS)
            print()
            main_menu()
        except BaseException as e:
            # Catch recursion error
            if "%s" % str(e):
                print(colored("Error: %s", "red") % str(e))
                main_menu()
            else:
                sys.exit()

    elif answers["Main Menu"] == "SQL Count":
        print()
        data_size()
        print()
        main_menu()

    elif answers["Main Menu"] == "SQL Reset":
        delete_data()
        main_menu()

    elif answers["Main Menu"] == "Visualization Menu":
        v_menu()

    elif answers["Main Menu"] == "Quit":
        sys.exit()


def main():
    """
    Calls main_menu()
    """

    main_menu()


if __name__ == "__main__":
    main()
