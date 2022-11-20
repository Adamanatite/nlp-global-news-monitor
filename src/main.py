from elasticsearch_database import CreateDB, GetActiveSources
from sources.newspaper3k_scraper import NewspaperScraper
from sources.feed_scraper import FeedScraper
import time

CreateDB()

def InitialiseActiveSources():
    for source in GetActiveSources():
        constructors = {"Web scraper": NewspaperScraper,
                        "RSS/Atom Feed": FeedScraper}

        scrapers = []

        scraper_type = source["_source"]["Data Source"]
        url = source["_source"]["URL"]
        name = source["_source"]["URL"]
        country = source["_source"]["URL"]
        lang = source["_source"]["URL"]

        if scraper_type in constructors.keys():
            scraper = constructors[scraper_type](url, name, country, lang)
            scrapers.append(scraper)

        return scrapers

with open("sources.txt") as f:
    # Parse source file
    scrapers = []
    
    i = 0

    for line in f:
        i += 1
        if i >= 11:
            break
        data = line.strip().split(" ")
        if len(data) == 1:
            current_lang = data[0]
            continue
        # Create source object
        source = NewspaperScraper(url=data[-5], name=" ".join(data[:-5]), country=data[-4], lang=current_lang)
        if source:
            scrapers.append(source)

with open("rss_feeds.txt") as f:
    for line in f:
        data = line.strip()
        # Create source object
        source = FeedScraper(url=data, name="Test", country="UK", lang="en")
        scrapers.append(source)

# scrapers = InitialiseActiveSources()

while True:
    #TODO: Functionality to remove disabled scrapers from scheduler
    for scraper in scrapers:
        if scraper.enabled:
            scraper.scrape()
    print("Sleeping...\n\n")
    time.sleep(120)