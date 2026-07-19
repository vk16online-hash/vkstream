import feedparser
import time

news_urls = ["https://www.motorsport.com/rss/f1/news/"]
dashboard_urls = [
    "https://www.motorsport.com/rss/f1/news/",
    "https://www.motorsport.com/rss/nascar-cup/news/",
    "https://www.motorsport.com/rss/motogp/news/",
    "https://www.motorsport.com/rss/wec/news/"
]

def update_files():
    # නිව්ස් බාර් එක සඳහා (News Bar)
    news_feed = feedparser.parse(news_urls[0])
    with open("news.txt", "w", encoding="utf-8") as f:
        f.write(" | ".join([entry.title for entry in news_feed.entries[:5]]))
    
    # දකුණු පැත්තේ ලිස්ට් එක සඳහා (Upcoming Races)
    dashboard_list = []
    for url in dashboard_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            dashboard_list.append(entry.title)
    
    with open("dashboard.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(dashboard_list[:15]))

while True:
    update_files()
    time.sleep(300) # මිනිත්තු 5කට සැරයක් අප්ඩේට් වේ
