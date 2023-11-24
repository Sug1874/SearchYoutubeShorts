import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
from youtube_fetcher import YoutubeFetcher
import datetime
from repo import save_spread_sheet

load_dotenv()
API_KEY = os.getenv('API_KEY')

param_file = open("params.json", "r")
params = json.load(param_file)

fetcher = YoutubeFetcher(API_KEY)

# キーワードでショートビデオを検索
def get_short_videos(pageToken=None):
    items, nextPageToken = fetcher.fetch_with_keyword(params["keyword"], params["onlyShort"], pageToken)
    if items == None:
        return None
    items = list(map(lambda item: {
                            "videoId": item["id"]["videoId"],
                            "title": item["snippet"]["title"],
                            "channelId": item["snippet"]["channelId"],
                        },
                items
                ))
    return items, nextPageToken

# チャンネル情報の取得
def get_channel_infos(items):
    channel_ids = map(lambda item: item["channelId"], items)
    channel_ids = set(channel_ids)

    channel_infos = fetcher.fetch_channels(channel_ids)
    channel_infos = list(map(
                        lambda channel: {
                                            "channelId": channel["id"],
                                            "customUrl": channel["snippet"]["customUrl"],
                                            "subscribers": channel["statistics"]["subscriberCount"],
                                            "uploadsPlaylistId": channel["contentDetails"]["relatedPlaylists"]["uploads"]
                                        },
                        channel_infos
                    ))
    return channel_infos

# チャンネルの登録者数でフィルタリング
def filter_with_subscribers(channel_info):
    num_subscribers = int(channel_info["subscribers"])
    min_subscribers = params["minSubscribers"]
    max_subscribers = params["maxSubscribers"]
    if min_subscribers > 0:
        if max_subscribers >0:
            return num_subscribers >= min_subscribers and num_subscribers <= max_subscribers
        else:
            return num_subscribers >= min_subscribers
    else:
        if max_subscribers >0:
            return num_subscribers <= max_subscribers
        else:
            return True

# 最後に動画投稿した日付の取得 
def get_latest_published_date(channel_infos):
    upload_playlists_ids = list(map(lambda channel: channel["uploadsPlaylistId"] , channel_infos))
    latest_videos = fetcher.fetch_latest_videos(upload_playlists_ids)
    latest_published_date = list(map(lambda video: video["snippet"]["publishedAt"] , latest_videos))
    return latest_published_date

# 最後に投稿した日からの経過日数でフィルタリング
def filter_with_elapsed_days(channel):
    if params["maxElapsedDays"] < 0:
        return True
    
    latest_post_datetime = datetime.datetime.strptime(channel["latestPublishedDate"], '%Y-%m-%dT%H:%M:%SZ')
    latest_post_date = datetime.date(latest_post_datetime.year, latest_post_datetime.month, latest_post_datetime.day)
    today = datetime.date.today()
    return (today - latest_post_date) <= datetime.timedelta(params["maxElapsedDays"])

# 動画の再生数、高評価数を取得
def get_video_statistics(items):
    video_ids = list(map(lambda item: item["videoId"], items))
    video_infos = fetcher.fetch_video_statistics(video_ids)

    def get_views_likes(info):
        result = {"views": None, "likes": None}
        if 'viewCount' in info["statistics"]:
            result["views"] = info["statistics"]["viewCount"]
        if 'likeCount' in info["statistics"]:
            result["likes"] = info["statistics"]["likeCount"]
        return result

    video_statistics = list(map(get_views_likes, video_infos))
    return video_statistics


def get_one_page_videos(pageToken=None):
    items, nextPageToken = get_short_videos(pageToken)

    if len(items) == 0:
        return [], nextPageToken

    channel_infos = get_channel_infos(items)
    channel_infos = list(filter(filter_with_subscribers, channel_infos))

    if len(channel_infos) == 0:
        return [], nextPageToken

    latest_published_date = get_latest_published_date(channel_infos)

    # 最新投稿日をchannel_infoに追加
    for channel, latest_date in zip(channel_infos, latest_published_date):
        channel["latestPublishedDate"] = latest_date
    
    channel_infos = list(filter(filter_with_elapsed_days, channel_infos))
    if len(channel_infos) == 0:
        return [], nextPageToken

    # 登録者、経過日数の条件を満たさない動画を除外
    remove_index = []
    for i, item in enumerate(items):
        flag = False
        for channel in channel_infos:
            if item["channelId"] == channel["channelId"]:
                flag = True
                item["customUrl"] = channel["customUrl"]
                item["subscribers"] = channel["subscribers"]
                item["latestPublishedDate"] = channel["latestPublishedDate"]
        if not flag:
            remove_index.append(i)
    
    for i in sorted(remove_index, reverse=True):
        items.pop(i)
 
    video_statistics = get_video_statistics(items)
    
    for item, statistics in zip(items, video_statistics):
        item["views"] = statistics["views"]
        item["likes"] = statistics["likes"]
    
    return items, nextPageToken


def main():
    nextPageToken = None
    all_items = []
    for i in range(params["maxPage"]):
        items, nextPageToken = get_one_page_videos(nextPageToken)
        all_items += items
        if not nextPageToken:
            break
    
    # Googleスプレッドシートに保存
    save_spread_sheet(all_items)

if __name__ == "__main__":
    main()