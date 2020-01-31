from bs4 import BeautifulSoup
import requests
import re
import csv
import sys
import argparse

def read_cl():
    parser = argparse.ArgumentParser()
    parser.add_argument('--imdb_id')
    args = parser.parse_args()
    return args

def get_show_seasons(show_id):
    show_url = f"https://www.imdb.com/title/tt0{show_id}/episodes"
    html = requests.get(show_url).text
    soup = BeautifulSoup(html)
    seasons = [x.text.strip() for x in soup.select("select#bySeason option")]
    return seasons

def get_season_episodes(show_id, season):
    episodes_url = f"https://www.imdb.com/title/tt0{show_id}/episodes/_ajax?season=" + season
    html = requests.get(episodes_url).text
    soup = BeautifulSoup(html)
    episodes = ([x["href"] for x in soup.select("div.eplist div.info > strong > a")])
    episode_ids = [re.findall("tt0(\d{6})",x)[0] for x in episodes]
    return episode_ids

if __name__ == "__main__":
    #FRIENDS_ID = "108778"
    args = read_cl()

    seasons = get_show_seasons(args.imdb_id)
    output_list = []
    for season in seasons:
        episode_ids = get_season_episodes(args.imdb_id, season)
        for i,id_ in enumerate(episode_ids):
            output_list.append({"season":season,"episode":str(i+1),"id":id_})
    writer = csv.DictWriter(sys.stdout, fieldnames=["season","episode","id"])
    writer.writeheader()
    for r in output_list:
        writer.writerow(r)
