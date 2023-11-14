import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
import csv
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

FIELDS = ["title", "link", "likes", "plays", "channel", "subscriber", "elapesed_days"]

def fetch_movie_list(keyword):
    '''
    YouTube APIで動画リストを取得
    '''
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        response = youtube.search().list(
            q=keyword,
            type='video',  
            part='id, snippet',
            maxResults=50,
        ).execute()
    except HttpError as e:
        print("Error occurred in calling API")
        print(e)
        return None
    else:
        return response["items"]

def search_movies(keyword, min_subscribers=-1, max_subscribers=-1, max_elapsed_days=-1):
    '''
    keywordをタイトル・ハッシュタグに含む動画を取得
    そのほかの引数で絞り込み（指定しない場合は負の値）
    '''
    items = fetch_movie_list(keyword)

    if items == None:
        return None

    items = filter_with_keyword(items, keyword)
    items = items.filter(lambda i: isShort(i["id"]["videoId"]))

    # 投稿者の情報取得
    channelIds = items.filter(lambda x: x["snippet"]["channelId"])


def filter_with_keyword(items, keyword):
    '''
    itemsの中からタイトル・ハッシュタグにkeywordを含む動画のみを抽出
    '''


def isShort(id):
    url = f"https://www.youtube.com/shorts/{id}"
    response = requests.get(url)
    return response.url == url

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
    result = search_movies(params["keyword"])

if __name__ == "__main__":
    main()