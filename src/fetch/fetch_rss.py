import os 
import json
import time
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Target RSS feeds
FEEDS = {
    "le_monde_politique" : "https://www.lemonde.fr/politique/rss_full.xml",
    "libération_politique" : "https://www.liberation.fr/arc/outboundfeeds/rss-all/category/politique/?outputType=xml"
}

def get_article_content(feed_name, url):

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, "html.parser")

        if feed_name == "le_monde_politique":
            paragraphs = soup.find_all("p", class_="article__paragraph")
            full_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        elif feed_name == "libération_politique":
            paragraphs = soup.find_all("p", class_="sc-cPiKLX AiZTS text-element")
            full_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        return full_text
    except Exception as e:
        print(f"[INFO] Error fetching content from {url}: {e}")
        return ""
    

def fetch_and_save_rss(feeds, output_dir="data/raw"):

    all_articles = []

    for feed_name, feed_url in feeds.items():
        print(f"Fetching RSS for: {feed_name} -> {feed_url}")
        parsed_feed = feedparser.parse(feed_url)

        for entry in parsed_feed.entries:
            title = entry.title if "title" in entry else "No Title" 
            link = entry.link if "link" in entry else "No Link"
            pubDate = entry.published if "published" in entry else "No Date"
            description = entry.description if "description" in entry else "No Description"
    
            full_text = get_article_content(feed_name, link)

            article_data = {
                "feed_name": feed_name,
                "title": title,
                "link": link,
                "pubDate": pubDate,
                "description": description,
                "content": full_text,
            }
            all_articles.append(article_data)

            time.sleep(1)

    # Saving everything in a timestamped json file. 
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_file = os.path.join(output_dir, f"french_politics_{timestamp}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] Saved {len(all_articles)} articles to {output_file}")

if __name__ == "__main__":
    fetch_and_save_rss(FEEDS)