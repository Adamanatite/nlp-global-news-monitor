from elasticsearch_database import CreateDB, GetActiveSources
from sources.newspaper3k_scraper import NewspaperScraper
from sources.feed_scraper import FeedScraper
import time

def InitialiseActiveSources():
    for source in GetActiveSources():
        constructors = {"Web scraper": NewspaperScraper,
                        "RSS/Atom Feed": FeedScraper}

        scrapers = []

        scraper_type = source["_source"]["Data Source"]
        url = source["_source"]["URL"]
        name = source["_source"]["Name"]
        country = source["_source"]["Country"]
        lang = source["_source"]["Language"]

        if scraper_type in constructors.keys():
            scraper = constructors[scraper_type](url, name, country, lang)
            scrapers.append(scraper)

        return scrapers

CreateDB()
scrapers = InitialiseActiveSources()

while True:
    #TODO: Functionality to remove disabled scrapers from scheduler
    for scraper in scrapers:
        if scraper.enabled:
            scraper.scrape()
    print("Sleeping...\n\n")
    time.sleep(120)