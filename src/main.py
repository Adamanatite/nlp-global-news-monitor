from elasticsearch_database import CreateDB, GetActiveSources
from sources.newspaper3k_scraper import NewspaperScraper
from sources.feed_scraper import FeedScraper
from sources.parse_config import ParseBoolean
import threading
import queue
import json
import random

with open("sources/config.json") as f:
    data = json.load(f)
    try: 
        USE_CONCURRENCY = ParseBoolean(data["concurrent"])
        NO_WORKERS = int(data["no_workers"])
        print(USE_CONCURRENCY)
    except Exception as e:
        print("Error in config")
        USE_CONCURRENCY=False

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

def scrape_sources(q, scrapers):
    while scrapers:
        for scraper in scrapers:
            if scraper.enabled:
                scraper.scrape()
            else:
                scrapers.pop(scraper)
        # Get new scraper from the queue
        scraper = q.get()
        if scraper:
            scrapers.append(scraper)


print(f"Beginning to scrape from {len(scrapers)} sources")
if USE_CONCURRENCY:
    random.shuffle(scrapers)
    
    # Split sources into threads
    n = len(scrapers) // NO_WORKERS
    threads = list()
    remaining = queue.Queue()
    for i in range(NO_WORKERS):
        x = threading.Thread(target=scrape_sources, args=(remaining,scrapers[n*i:n*(i+1)]))
        threads.append(x)
        x.start()
    # Create queue of newly activated sources
    for elt in scrapers[n*NO_WORKERS:]:
        remaining.put(elt)
    
    for t in threads:
        t.join()
else:
    while scrapers:
        for scraper in scrapers:
            if scraper.enabled:
                scraper.scrape()
            else:
                scrapers.pop(scraper)