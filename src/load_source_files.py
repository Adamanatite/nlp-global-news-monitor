from sources.newspaper3k_scraper import NewspaperScraper
from sources.feed_scraper import FeedScraper
from elasticsearch_database import AddSource

with open("sources.txt", encoding="utf8") as f:
    # Parse source file
    scrapers = []

    for line in f:
        data = line.strip().split(" ")
        if len(data) == 1:
            current_lang = data[0]
            continue
        # Create source object
        AddSource(data[-5], " ".join(data[:-5]), data[-4], current_lang, "Web scraper")

with open("rss_feeds.txt") as f:
    for line in f:
        data = line.strip().split(",")
        # Create source object
        #TODO: Manually do country or workout way to automatically do country
        AddSource(data[1], data[2], None, data[3], "RSS/Atom Feed")