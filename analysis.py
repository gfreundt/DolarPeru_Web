import csv
import matplotlib.pyplot as plt
import datetime as dt
import wget
import sys
import os
import tweepy
import time
from datetime import datetime as dt


def load_data(filename):
	with open(filename, mode='r') as file:
		data = [i for i in csv.reader(file, delimiter=',')]
	return [[i[0], i[1], (dt.strptime(i[2], '%Y-%m-%d %H:%M:%S')-dt.strptime(data[0][2], '%Y-%m-%d %H:%M:%S')).total_seconds()/1440] for i in data]

def process(data):
	unique_url = list(set([i[0] for i in data]))
	pdata = [[[i[2], float(i[1])] for i in data if i[0] == unique] for unique in unique_url]
	return unique_url, pdata


def tweet(data, status, type):
    # Check if option to skip tweet active
    if "NOTWEET" in [i.upper() for i in sys.argv]:
        return

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("aNZyEv2YACLxzTb9v8lZxknxJ", "5larD1pQf7W8ycC9LKdX9UcjGO3O3u43XCRGub0jwjdseMpyEa")
    auth.set_access_token("51777181-UrK6HYo3Qn79CYSAF9P1Ujshv2zwemJZsMd85xV7h",
                          "nUkMPltjRw3a1NoH5iwYxsgs2DFcH1dsvBSGa8SR1n0HC")
    # Create API object
    api = tweepy.API(auth)

    if type == 'image':  # Upload images and get media_ids in blocks of 4
        blocks = [[i for i in data[k:k + 4]] for k in range(0, len(data), 4)]
        for k, data in enumerate(blocks):
            media_ids = []
            for filename in data:
                res = api.media_upload(filename)
                media_ids.append(res.media_id)
            # Tweet block of 4 (or less) images
            if k == 0:
                tweet = api.update_status(status=status + '1/' + str(len(blocks)), media_ids=media_ids)
                status_id = tweet.id_str
            else:
                api.update_status(status=status + ' ' + str(k + 1) + '/' + str(len(blocks)), media_ids=media_ids,
                                  in_reply_to_status_id=status_id)
    elif type == 'text':  # text only tweet in status then reply format
        try:
            for k, each_tweet in enumerate(data):
                if k == 0:
                    tweet = api.update_status(status=each_tweet)
                    status_id = tweet.id_str
                else:
                    api.update_status(status=each_tweet, in_reply_to_status_id=status_id)
        except:
            print('Twitter Error')



def plot(urls, data):
    plt.rcParams['figure.figsize'] = (16, 10)
    for title, series in zip(urls, data):
        plt.plot(series[:], label=title)
        print(series)

    # plt.get_current_fig_manager().window.state('zoomed')
    plt.axis([3.5, 365, 3.7, 3.85])
    plt.autoscale(axis='x')
    plt.legend(loc='upper right')
    plt.ylabel('Tipo de Cambio')
    plt.suptitle('TdC', size='xx-large', y=.98)
    plt.grid(axis='y')

    plt.show()
    plt.close('all')


urls, data = process(load_data('TDC.txt'))
plot(urls, data)