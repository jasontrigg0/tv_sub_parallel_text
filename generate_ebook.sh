FRIENDS_IMDB_ID=108778
python scrape_tv_show_episode_ids.py --imdb_id $FRIENDS_IMDB_ID > /tmp/episodes.csv
python align_imdb_code.py --episode_csv /tmp/episodes.csv
python alignment_to_html.py > /tmp/book.html
ebook-convert /tmp/book.html /tmp/friends.epub
