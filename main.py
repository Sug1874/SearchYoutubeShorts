import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
import csv
from dotenv import load_dotenv
import os
from youtube_fetcher import YoutubeFetcher

load_dotenv()
API_KEY = os.getenv('API_KEY')

FIELDS = ["title", "link", "likes", "plays", "channel", "subscriber", "elapesed_days"]


def filter_with_subscribers(items, max_subscribers, min_subscribers):
    '''
    itemsの中から登録者数の条件を満たすものだけを抽出
    '''

def filter_with_elapsed_days(items, maxElapsedDays):
    '''
    itemsの中から最終投稿日からの経過日数の条件を満たすものだけを抽出
    '''


def save_csv(data):
    with open('./outputs/output.csv', 'w') as f: 
        csv_writer = csv.writer(f)
        csv_writer.writerows(data)


def main():
    param_file = open("params.json", "r")
    params = json.load(param_file)

    fetcher = YoutubeFetcher(API_KEY)
    items = fetcher.fetch_with_keyword(params.keyword, True)

    

if __name__ == "__main__":
    main()