import os
import requests


def fetch_file_from_twic(week_number: int):
    base_url = f"https://theweekinchess.com/zips/twic{week_number}g.zip"
    a = requests.get(base_url, headers={'Accept': '*/*', "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})

def unzip_file(zip_file):
    pass

def clean_up_file():
    pass

def main():
    for week in range(last_week_downloaded, this_week):
        fetch_file_from_twic(week)
        unzip_file(week)

if __name__ == "__main__":
    last_week_downloaded: int = 919
    this_week: int = 1442
    target_path: str = "D:\Documents\ChessBase\\"
    append_to_existing_database: bool = False
    main()