from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

class YoutubeFetcher():
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def fetch_with_keyword(self, keyword, only_short=True):
        try:
            response = self.youtube.search().list(
                q=keyword,
                type='video',  
                part='id, snippet',
                maxResults=50,
                videoDuration='short',
            ).execute()

            items = response["items"]

            if only_short:
                items = items.filter(lambda item: self.isShort(item.id.videoId))
            return items
        except HttpError as e:
            print("Error occurred in calling API")
            print(e)
            return None
        
    def isShort(movie_id):
        url = f"https://www.youtube.com/shorts/{movie_id}"
        response = requests.get(url)
        return response.url == url

    
    def fetch_channels(self, channel_ids):
        pass

    def fetch_playlists(self, playlist_ids):
        pass

    

