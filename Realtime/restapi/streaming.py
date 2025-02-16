#!/usr/bin/python2.7

#Future
from __future__ import absolute_import, print_function

#Imports sys to change path
import sys

#database
import sqlite3
import time


sys.path.insert(1,'/home/nbroeking/DataMining/tweepy')
sys.path.insert(1,'/home/nbroeking//DataMining/loot/dist-packages')
#Import Tweepy

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#JSON
import json
import ast

from classifier import extractFeatures, getFeatureVector, PreprocessTweet, train

# Consumer Keys
consumer_key="44vVVicDrIDrA9iJ6FHCUA0TB"
consumer_secret="tyeyRqSJkHrUjec2sdO5tiIJeMb5Sk5OZVySeN9CIEoXOFcvtn"

access_token="52314456-zHY3UfyiQ6KVrWrgMLy4nGmPzInaFmxsZVXhKCHfO"
access_token_secret="zYsjeIH7TKxeJnHxVHwg3HVUynu4JZgKLvfhsUR0Hn7Qh"

import socket

broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast_sock.bind(('127.0.0.1', 5483)) # this should only listen on localhost

to_addr = ('127.0.0.1', 5551)

#Listen for tweets
class TweetListener(StreamListener):
    def __init__(self):
        
        self.db = sqlite3.connect('Twitter.db')
        cursor = self.db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Tweets(id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, retweeted BOOL, retweeted_count INT, time TEXT, userid INT, tweetId INT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY AUTOINCREMENT, userid INT, followers_count INT, friendcount INT, name TEXT)''')
        self.db.commit()

        self.classifier = train()

    def on_data(self, data):
        json_data = json.loads(data)
	if "text" in json_data:
            text = json_data["text"]
            clazz = self.classifier.classify(
                        extractFeatures(
                            getFeatureVector(
                                PreprocessTweet(text)
                                )))

            broadcast_sock.sendto(json.dumps({'text': text, 'sentiment': clazz}), to_addr)

#Main Function
if __name__ == '__main__':
    while True:
        l = TweetListener()
        try:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
           
            stream = Stream(auth, l)
            stream.filter(track=['google', 'apple', 'oracle','amazon', 'IBM', 'Google', 'Apple', 'Oracle', 'Amazon', 'ibm', 'Shell', 'shell' ])

        except:
	    print ("There was an exception")
