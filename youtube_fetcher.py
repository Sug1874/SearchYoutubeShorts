from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

class YoutubeFetcher():
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def fetch_with_keyword(self, keyword, only_short=True, pageToken=None):
        try:
            if pageToken:
                response = self.youtube.search().list(
                    q=keyword,
                    type='video',  
                    part='id, snippet',
                    maxResults=10,
                    videoDuration='short',
                    pageToken = pageToken
                ).execute()
            else:
                response = self.youtube.search().list(
                    q=keyword,
                    type='video',  
                    part='id, snippet',
                    maxResults=10,
                    videoDuration='short',
                ).execute()
            items = response["items"]
            nextPageToken = response["nextPageToken"]

            if only_short:
                items = list(filter(lambda item: self.isShort(item["id"]["videoId"]), items))
            return items, nextPageToken
        except HttpError as e:
            print("Error occurred in calling API")
            print(e)
            return None
        
    def isShort(self, movie_id):
        url = f"https://www.youtube.com/shorts/{movie_id}"
        response = requests.get(url)
        return response.url == url

    
    def fetch_channels(self, channel_ids):
        try:
            response = self.youtube.channels().list(
                part = "id, snippet, contentDetails, statistics",
                id = ','.join(channel_ids),
                maxResults = 50
            ).execute()
            items = response["items"]
            return items
        except HttpError as e:
            print("Error occurred in calling API")
            print(e)
            return None
        

    def fetch_latest_videos(self, playlist_ids):
        items = []
        for id in playlist_ids:
            response = self.youtube.playlistItems().list(
                part = 'snippet',
                playlistId = id,
                maxResults = 1
            ).execute()
            items.append(response['items'][0])
        return items
    
    def fetch_video_statistics(self, video_ids):
        response = self.youtube.videos().list(
            part = 'statistics',
            id = ','.join(video_ids),
            maxResults = 50,
        ).execute()
        return response["items"]


    

