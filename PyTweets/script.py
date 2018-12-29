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


class myListener(tweepy.StreamListener):
    def on_connect(self):
        print(colored("Successfully connected to Twitter", "green"))

    def __init__(self, api=None):
        self.num_tweets = 0
        self.total_tweets = int(input("Number of tweets:"))
        self.pbar = tqdm(total=self.total_tweets)
        self.unsaved = 0
        self.emojis = 0

    def on_data(self, data):

        try:
            portalA = creds()
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
                query = "INSERT INTO PyData (screen_name, created_at, location, followers_count, text) VALUES (%s,%s,%s,%s,%s)"
                portalA[1].execute(
                    query, (screen_name, created_at, location, followers_count, text))
                portalA[0].commit()
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
                print(colored("Contained Emojis: "
                              + str(self.emojis) + "\n", "green"))
            else:
                "\n"
            return False

    def on_error(self, status):
        print("An error has occured: " + repr(status))
        return True


def creds():
    cnxt = db.connect(user="root", password="u0bj8dsvs1n",
                      host="localhost",
                      database="sys",
                      charset="utf8mb4")
    cursor = cnxt.cursor()
    return cnxt, cursor


def deleteData():
    ask = input("Reset PyData? [yn]")
    if ask == "y" or ask == "Y":
        try:
            portalB = creds()
            cursor = portalB[0].cursor()
            delete = "truncate PyData"
            cursor.execute(delete)
            remainder = cursor.execute("SELECT * FROM PyData ")
            print(colored("Remaining rows: " + str(remainder), "green"))
        except BaseException as e:
            print(colored("Error on_data: %s", "red") % str(e))
    elif ask == "n" or ask == "N":
        mainMenu()


def processData():
    portalC = creds()
    cursor = portalC[0].cursor()
    cursor.execute(
        "SELECT screen_name, created_at, location, followers_count, text FROM PyData ORDER BY created_at DESC")
    rows = cursor.fetchall()
    # Restruces data into pandas datafram for easy use
    processed = pd.DataFrame([[ij for ij in i] for i in rows])
    processed.rename(columns={0: "Username", 1: "Created at",
                              2: "Location", 3: "Followers", 4: "Text"}, inplace=True)
    return processed


def getDataSize():
    processed = processData()
    print("Tweets: " + str(len(processed)))


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def pieChart(pieData):
    # Create init pie chart
    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    pieTerms = len(pieData)
    for i in range(len(pieData)):
        analysis = TextBlob(pieData["Text"][i])
        polarity += analysis.sentiment.polarity
        if(analysis.sentiment.polarity > 0.00):
            positive += 1
        elif(analysis.sentiment.polarity < 0.00):
            negative += 1
        elif(analysis.sentiment.polarity == 0):
            neutral += 1
    positive = percentage(positive, pieTerms)
    negative = percentage(negative, pieTerms)
    neutral = percentage(neutral, pieTerms)
    labels = ["Positive [" + str(round(positive)) + "%]", "Negative [" + str(round(negative)) + "%]",
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


def heatMap(heatData):
    polList, folList, folCountList, polCountList, pol_tots = [], [], [], [], []
    polTotA, polTotB, polTotC, polTotD, polTotE = 0, 0, 0, 0, 0
    folCountA, folCountB, folCountC, folCountD, folCountE = 0, 0, 0, 0, 0
    polCountA, polCountB, polCountC, polCountD, polCountE = 0, 0, 0, 0, 0
    for i in range(len(heatData)):
        polarity = TextBlob(heatData["Text"][i]).sentiment.polarity
        followers = heatData["Followers"][i]
        # create list of polarities and followers from each user
        polList.append(polarity)
        folList.append(followers)
    for i in range(len(heatData)):
        # update Follower counts
        # save polarities in each follower group for later averaging
        if folList[i] < 10**1 and folList[i] >= 0:
            folCountA += 1
            polTotA += round(TextBlob(heatData["Text"]
                                      [i]).sentiment.polarity, 2)

        elif folList[i] < 10**2 and folList[i] >= 10**1:
            folCountB += 1
            polTotB += round(TextBlob(heatData["Text"]
                                      [i]).sentiment.polarity, 2)

        elif folList[i] < 10**3 and folList[i] >= 10**2:
            folCountC += 1
            polTotC += round(TextBlob(heatData["Text"]
                                      [i]).sentiment.polarity, 2)

        elif folList[i] < 10**4 and folList[i] >= 10**3:
            folCountD += 1
            polTotD += round(TextBlob(heatData["Text"]
                                      [i]).sentiment.polarity, 2)

        elif folList[i] >= 10**4:
            folCountE += 1
            polTotE += round(TextBlob(heatData["Text"]
                                      [i]).sentiment.polarity, 2)

        # update Polarity counts
        if polList[i] < -1.6:
            polCountA += 1

        elif polList[i] > -1.6 and polList[i] < -0.6:
            polCountB += 1

        elif polList[i] > -0.6 and polList[i] < 0.6:
            polCountC += 1

        elif polList[i] > 0.6 and polList[i] < 1.6:
            polCountD += 1

        else:
            polCountE += 1
    # create y axis data containing count of followers that fall in each interval
    folCountList.extend(
        [folCountA, folCountB, folCountC, folCountD, folCountE])
    # create x axis data containing count of polarities that fall in each interval
    polCountList.extend(
        [polCountA, polCountB, polCountC, polCountD, polCountE])
    pol_tots.extend([round(polTotA, 2), round(polTotB, 2), round(
        polTotC, 2), round(polTotD, 2), round(polTotE, 2)])
    r1, r2, r3, r4, r5 = [], [], [], [], []
    rows = [r1, r2, r3, r4, r5]
    # create each row with calculated averages
    for i in range(len(rows)):
        for j in polCountList:
            if j == 0:
                rows[i].append(0.0)
            else:
                rows[i].append(round((pol_tots[i] / j), 3))

    df = pd.DataFrame(rows, folCountList, polCountList)
    sns.heatmap(df, annot=True, fmt="g", cmap='viridis')
    plt.title("Average Sentiment Polarity by Group")
    plt.ylabel("hello")
    plt.ylabel('10,000     10,000     1,000     100     10')
    plt.xlabel(
        '-2.0             -1.0             0.0             1.0             2.0')
    plt.show()


def sentiMap(sentiData):
    portalD = creds()
    cursor = portalD[0].cursor()
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
        cordsCount = 0
        sentibar = tqdm(total=count)
        cluster = folium.plugins.MarkerCluster().add_to(mapvar)
        for i in range(count):
            location = geolocator.geocode(sentiData["Location"][i])
            if location:
                polarity = TextBlob(sentiData["Text"][i]).sentiment.polarity
                if polarity > 0.0:
                    econ = folium.Icon(color="green")
                elif polarity < 0.0:
                    econ = folium.Icon(color="red")
                elif polarity == 0.0:
                    econ = folium.Icon(color="orange")
                folium.Marker(popup="@" + sentiData["Username"][i] + ": " + sentiData["Text"][i] +
                              " Followers: " +
                              str(sentiData["Followers"][i]) +
                              " Created at: " +
                              str(sentiData["Created at"][i]),
                              location=[location.latitude, location.longitude], icon=econ).add_to(cluster)
            cordsCount += 1
            sentibar.update(1)
        sentibar.close()
        mapvar.save("sentimap.html")
        print(colored("Click markers for more details", "green"))
        vMenu()
    except BaseException as e:
        print(colored("Geocoder Error: %s", "red") % str(e))


def vMenu():
    vizData = processData()
    questions = [
        inquirer.List("visuals",
                      message="Which visualization do you need?",
                      choices=["Pie Chart", "Senti Map", "Heat Map",
                               "Back", "Quit"],
                      ),
    ]
    answers = inquirer.prompt(questions)
    if answers["visuals"] == "Pie Chart":
        pieChart(vizData)
    elif answers["visuals"] == "Senti Map":
        sentiMap(vizData)
    elif answers["visuals"] == "Heat Map":
        heatMap(vizData)
    elif answers["visuals"] == "Back":
        if __name__ == "__main__":
            main()
    elif answers["visuals"] == "Quit":
        sys.exit()


def mainMenu():
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
        go = input("Stream? [yn]")
        if (go == "y" or go == "Y"):
            twitterStream = Stream(auth, myListener())
            twitterStream.filter(track=WORDS)
            mainMenu()
        elif (go == "n" or go == "N"):
            mainMenu()

    elif answers["Main Menu"] == "Add Terms":
        if "WORDS" in locals() or "WORDS" in globals():
            pass
        else:
            WORDS = []
        while(True):
            newTerm = input("New Term: ")
            WORDS.append(newTerm)
            print("Current List: ", WORDS)
            go = input("Stream? [yn]")
            if (go == "y" or go == "Y"):
                twitterStream = Stream(auth, myListener())
                twitterStream.filter(track=WORDS)
                mainMenu()
            elif (go == "n" or go == "N"):
                print()
                print("Current List: ", WORDS)
                print()
                mainMenu()
    elif answers["Main Menu"] == "Stream":
        try:
            go = input("Stream? [yn]")
            if (go == "y" or go == "Y"):
                twitterStream = Stream(auth, myListener())
                twitterStream.filter(track=WORDS)
                mainMenu()
            elif (go == "n" or go == "N"):
                print()
                print("Current List: ", WORDS)
                print()
                mainMenu()
        except BaseException as e:
            print(colored("Error on_data: %s", "red") % str(e))
            mainMenu()

    elif answers["Main Menu"] == "Get Words":
        try:
            print()
            print("Current List: ", WORDS)
            print()
            mainMenu()
        except BaseException as e:
            print(colored("Error on_data: %s", "red") % str(e))
            mainMenu()

    elif answers["Main Menu"] == "SQL Count":
        print()
        getDataSize()
        print()
        mainMenu()

    elif answers["Main Menu"] == "SQL Reset":
        deleteData()

    elif answers["Main Menu"] == "Visualization Menu":
        vMenu()

    elif answers["Main Menu"] == "Quit":
        sys.exit()


def main():
    mainMenu()


if __name__ == "__main__":
    main()
