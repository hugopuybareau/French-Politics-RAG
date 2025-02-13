# Tests for fetch_rss.py

import feedparser
from src.fetch.fetch_rss import (
    get_article_content,
    fetch_and_save_rss
)

# Target RSS feeds
FEEDS = {
    "le_monde_politique" : "https://www.lemonde.fr/politique/rss_full.xml",
    # "libération_politique" : "https://www.liberation.fr/rss/politiques/"
}

def test_fetch():
    