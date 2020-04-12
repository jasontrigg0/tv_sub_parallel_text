FRIENDS_IMDB_ID=108778
EBOOK_TITLE=Friends

python scrape_tv_show_episode_ids.py --imdb_id $FRIENDS_IMDB_ID > /tmp/episodes.csv
python align_imdb_code.py --episode_csv /tmp/episodes.csv
python alignment_to_html.py --title $EBOOK_TITLE > /tmp/book.html
ebook-convert /tmp/book.html /tmp/$EBOOK_TITLE.mobi --chapter "//h:h2" --level1-toc '//h:h1' --level2-toc '//h:h2'  --mobi-file-type new
