import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
import csv
from dotenv import load_dotenv
import os
from youtube_fetcher import YoutubeFetcher
import datetime

load_dotenv()
API_KEY = os.getenv('API_KEY')

FIELDS = ["title", "link", "likes", "plays", "channel", "subscriber", "elapesed_days"]


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
    items = map(lambda item: {
                            "video_id": item["id"]["videoId"],
                            "title": item["snippet"]["title"],
                            "channel_id": item["snippet"]["channelId"],
                        },
                items
                )
    
    # チャンネル情報の取得
    channel_ids = map(lambda item: item["channelId"], items)
    channel_ids = set(channel_ids)
    channel_infos = fetcher.fetch_channels(channel_ids)
    channel_infos = map(
                        lambda channel: {
                                            "channel_id": channel["id"],
                                            "subscribers": channel["statistics"]["subscriberCount"],
                                            "uploads_playlist_id": channel["contentDetails"]["uploads"]
                                        },
                        channel_infos
                    )

    # 登録者数でフィルタリング
    def filter_with_subscribers(channel_info):
        num_subscribers = channel_info["subscribers"]
        return num_subscribers >= params.minSubscribers and num_subscribers <= params["maxSubscribers"]
    channel_infos = channel_infos.filter(filter_with_subscribers)

    # 最新投稿日の取得
    upload_playlists_ids = map(lambda channel: channel["uploads_playlist_id"] , channel_infos)
    latest_videos = fetcher.fetch_latest_videos(upload_playlists_ids)
    latest_published_date = map(lambda video: video["snippet"]["publishedAt"] , channel_infos)

    # 最新投稿日をchannel_infoに追加
    for channel, latest_date in zip(channel_infos, latest_published_date):
        channel["latest_published_date"] = latest_date

    def filter_with_elapsed_days(channel):
        latest_post_datetime = datetime.datetime.strptime(channel["latest_published_date"], '%Y-%m-%dT%H:%M:%S')
        latest_post_date = datetime.date(latest_post_datetime.year, latest_post_datetime.month, latest_post_datetime.day)
        today = datetime.date.today()
        return (today - latest_post_date) <= datetime.timedelta(params["maxElapsedDays"])
    
    channel_infos = channel_infos.filter(filter_with_elapsed_days)

    remove_index = []
    for item, i in enumerate(items):
        flag = False
        for channel in channel_infos:
            if item["channel_id"] == channel["channel_id"]:
                flag = True
                item["subscribers"] = channel["subscribers"]
                item["latest_published_date"] = channel["latest_published_date"]
        if not flag:
            remove_index.append(i)
    
    for i in sorted(remove_index, reverse=True):
        items.pop(i)
    
    video_ids = map(lambda item: item["video_id"], items)
    video_infos = fetcher.fetch_video_statistics(video_ids)
    video_statistics = map(lambda info: {
                                            "views": info["statistics"]["viewCount"],
                                            "likes": info["statistics"]["likeCount"]
                                        }
                            ,video_infos
                            )
    
    for item, statistics in zip(items, video_statistics):
        item["views"] = statistics["views"]
        item["likes"] = statistics["likes"]
    
    save_csv(items)
    


        



if __name__ == "__main__":
    main()