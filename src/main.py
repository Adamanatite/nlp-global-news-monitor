from elasticsearch_database import CreateDB, GetActiveSources
from sources.newspaper3k_scraper import NewspaperScraper
from sources.feed_scraper import FeedScraper

def InitialiseActiveSources():
    scrapers = []
    constructors = {"Web scraper": NewspaperScraper,
                    "RSS/Atom Feed": FeedScraper}

    for source in GetActiveSources():
        source_id = source["_id"]
        scraper_type = source["_source"]["Data Source"]
        url = source["_source"]["URL"]
        name = source["_source"]["Name"]
        country = source["_source"]["Country"]
        lang = source["_source"]["Language"]
        last_scrape_time = source["_source"]["Last Retrieved"]
        try:
            scraper = constructors[scraper_type](url, name, country, lang, source_id, last_scrape_time)
            scrapers.append(scraper)
        except Exception as e:
            print(str(e))
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
    #TODO: Rate limiting system
    print("Completed one loop. Checking again...")