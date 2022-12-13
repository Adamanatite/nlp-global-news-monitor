from elasticsearch_database import CreateDB, GetActiveSources
from scrapers.newspaper3k_scraper import NewspaperScraper
from scrapers.feed_scraper import FeedScraper
from utils.parse_config import ParseBoolean
import threading
import queue
import json
import random
from datetime import datetime
import time

with open("data/config.json") as f:
    data = json.load(f)
    try: 
        USE_CONCURRENCY = ParseBoolean(data["concurrent"])
        NO_WORKERS = int(data["no_workers"])
        MIN_SECONDS_PER_SCRAPE = int(data["min_seconds_per_scrape"])
    except Exception as e:
        print("Error in config")
        USE_CONCURRENCY=False
        MIN_SECONDS_PER_SCRAPE = 300

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

def scrape_sources(id, q, scrapers):
    while scrapers:
        begin_time = datetime.now()

        # Go through scraper list
        for i, scraper in enumerate(scrapers):
            if scraper.enabled:
                scraper.scrape()
            else:
                print(f'[{id}] Disabling scraper {scraper.name}')
                scrapers.pop(i)

        # Get new scraper from the queue
        try:
            scraper = q.get(False)
            if scraper:
                print(f'[{id}] Added {scraper.name} to list')
                scrapers.append(scraper) 
        except queue.Empty:
            pass

        # Wait minimum time
        time_elapsed = (datetime.now() - begin_time).seconds
        if time_elapsed < MIN_SECONDS_PER_SCRAPE:
            time_remaining = MIN_SECONDS_PER_SCRAPE - time_elapsed
            print(f"[{id}] Sleeping for {time_remaining} seconds...")
            time.sleep(time_remaining)


# Main function
print(f"Beginning to scrape from {len(scrapers)} sources")
if USE_CONCURRENCY:
    random.shuffle(scrapers)
    
    # Split sources into threads
    n = len(scrapers) // NO_WORKERS
    threads = list()
    remaining = queue.Queue()
    # Create queue of newly activated sources
    for elt in scrapers[n*NO_WORKERS:]:
        remaining.put(elt)
    # Start threads
    for i in range(NO_WORKERS):
        x = threading.Thread(target=scrape_sources, args=(i,remaining,scrapers[n*i:n*(i+1)]))
        threads.append(x)
        x.start()

    for t in threads:
        t.join()
else:
    # Non-concurrent version
    while scrapers:
        for scraper in scrapers:
            if scraper.enabled:
                scraper.scrape()
            else:
                scrapers.pop(scraper)