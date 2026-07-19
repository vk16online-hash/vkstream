import time

# මෙතනට ඔබේ නිව්ස් එක එන ඕනෑම API එකක කෝඩ් එකක් දාන්න පුළුවන්
# අපි දැනට නිකන් උදාහරණයක් විදියට මේක හදමු
def get_latest_news():
    # මෙතනට ඔබේ දත්ත එන ස්ක්‍රිප්ට් එක ලියන්න (උදා: F1/Motorsport news)
    return "🚀 Motorsport Live: Max Verstappen P1 | Next Race: Spa | Data updated at " + time.strftime("%H:%M:%S")

while True:
    news = get_latest_news()
    with open("news.txt", "w", encoding="utf-8") as f:
        f.write(news)
    time.sleep(30) # විනාඩි 1/2කට සැරයක් අප්ඩේට් වෙනවා
