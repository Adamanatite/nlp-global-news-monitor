from elasticsearch_database import CreateDB, GetActiveSources
from sources.newspaper3k_scraper import NewspaperScraper
from sources.feed_scraper import FeedScraper
import time

def InitialiseActiveSources():
    scrapers = []
    constructors = {"Web scraper": NewspaperScraper,
                    "RSS/Atom Feed": FeedScraper}

    for source in GetActiveSources():
        scraper_type = source["_source"]["Data Source"]
        url = source["_source"]["URL"]
        name = source["_source"]["Name"]
        country = source["_source"]["Country"]
        lang = source["_source"]["Language"]

        try:
            scraper = constructors[scraper_type](url, name, country, lang)
            scrapers.append(scraper)
        except:
            continue

    return scrapers

CreateDB()
scrapers = InitialiseActiveSources()

print(f"Beginning to scrape from {len(scrapers)} sources")
while True:
    #TODO: Functionality to remove disabled scrapers from scheduler
    for scraper in scrapers:
        if scraper.enabled:
            scraper.scrape()
    print("Sleeping...\n\n")
    time.sleep(120)