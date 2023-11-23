from google.oauth2.service_account import Credentials
import gspread
from gspread_formatting import *
import datetime
import csv
import os
from dotenv import load_dotenv

FIELDS = ["タイトル", "動画リンク", "高評価数", "再生回数", "チャンネルリンク", "登録者数", "最後に投稿した日"]

load_dotenv()
FOLDER_ID = os.getenv('FOLDER_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

scopes = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Credentials 情報を取得
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=scopes
)
gc = gspread.authorize(credentials)

def save_spread_sheet(items):
    data = list(map(lambda item: [
                                item["title"],
                                f"https://www.youtube.com/shorts/{item['videoId']}",
                                item["likes"],
                                item["views"],
                                f"https://www.youtube.com/{item['customUrl']}",
                                item["subscribers"],
                                datetime.datetime.strptime(item["latestPublishedDate"], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y年%m月%d日")
                            ], 
                            items
                    )
                )
    data.insert(0, FIELDS)

    file_name = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    workbook = gc.create(file_name, FOLDER_ID)

    sheet = workbook.get_worksheet(0)
    sheet.update(f'A1:G{len(data)}', data)

    fmt = CellFormat(
        backgroundColor=Color(0, 0.8, 1.0),
        textFormat=TextFormat(bold=True),
        horizontalAlignment='CENTER'
    )
    format_cell_range(sheet, 'A1:G1', fmt)
    Color()
    return




def save_csv(items):
    data = list(map(lambda item: [
                                item["title"],
                                f"https://www.youtube.com/shorts/{item['videoId']}",
                                item["likes"],
                                item["views"],
                                f"https://www.youtube.com/{item['customUrl']}",
                                item["subscribers"],
                                datetime.datetime.strptime(item["latestPublishedDate"], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y年%m月%d日")
                            ], 
                            items
                    )
                )
    data.insert(0, FIELDS)
    
    now = datetime.datetime.today()
    file_name = now.strftime('%Y%m%d%H%M%S')

    with open(f"./outputs/{file_name}.csv", 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(data)