import feedparser
import time

# අපේ ප්‍රධාන පුවත් මූලාශ්‍ර
feeds = [
    "https://www.motorsport.com/rss/f1/news/",
    "https://www.autosport.com/rss/feed/f1",
    "https://www.crash.net/rss/f1"
]

def fetch_latest_news():
    news_list = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]: # සෑම සයිට් එකකින්ම නිව්ස් 5ක්
            news_list.append(entry.title)
    
    # පේළි 15ක් පමණක් තෝරා ගැනීම
    return news_list[:15]

while True:
    try:
        latest_news = fetch_latest_news()
        with open("news.txt", "w", encoding="utf-8") as f:
            for item in latest_news:
                f.write(item + "  |  ") # නිව්ස් එකින් එක ස්ක්‍රෝල් වෙන්න
    except:
        pass
    time.sleep(300) # මිනිත්තු 5කට සැරයක් අලුත් නිව්ස් ඔටෝම හොයනවා
