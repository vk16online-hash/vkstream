import feedparser
import time

news_url = "https://www.motorsport.com/rss/f1/news/"
dashboard_urls = [
    "https://www.motorsport.com/rss/f1/news/",
    "https://www.motorsport.com/rss/nascar-cup/news/",
    "https://www.motorsport.com/rss/motogp/news/"
]

def update_files():
    # නිව්ස් බාර් එක
    feed = feedparser.parse(news_url)
    with open("news.txt", "w", encoding="utf-8") as f:
        f.write(" | ".join([entry.title for entry in feed.entries[:5]]))
    
    # දකුණු පැත්තේ පුවරුව (පේළි 10)
    race_list = []
    for url in dashboard_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:4]:
            race_list.append(entry.title[:30]) 
    
    with open("dashboard.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(race_list[:10]))

while True:
    update_files()
    time.sleep(600)
