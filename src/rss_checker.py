import feedparser

urls=[]

with open("rss_feeds.txt", encoding="utf8") as f:
    for line in f:
        data = line.strip().split(",")
        urls.append(data[1])

for url in urls:
    unique_feed_keys = set()
    unique_article_keys = set()
    d = feedparser.parse(url)
    unique_feed_keys.update(d.feed.keys())
    if d.entries:
        unique_article_keys.update(d.entries[0].keys())

print(unique_feed_keys)
print(unique_article_keys)