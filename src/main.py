from database.elasticsearch_database import CreateDB, GetAllSources, AddArticles
from scrapers.newspaper3k_scraper import NewspaperScraper
from scrapers.feed_scraper import FeedScraper
from utils.parse_config import ParseBoolean
from classifier.BERTClassifier import BERTClassifier
import threading
import queue
import json
import random
from datetime import datetime
import time
import eel


with open("config.json", encoding="utf-8") as f:
    data = json.load(f)
    try: 
        USE_CONCURRENCY = ParseBoolean(data["concurrent"])
        TRAIN_MODEL = ParseBoolean(data["train_model"])
        NO_WORKERS = int(data["no_workers"])
        MIN_SECONDS_PER_SCRAPE = int(data["min_seconds_per_scrape"])
        MAX_ACTIVE_SCRAPERS = int(data["max_active_scrapers"])
        EMPTY_DAYS_UNTIL_STALE = int(data["empty_days_until_stale"])
    except Exception as e:
        print("Error in config.json file")
        USE_CONCURRENCY=False
        MIN_SECONDS_PER_SCRAPE = 300
        MAX_ACTIVE_SCRAPERS = 1000
        EMPTY_DAYS_UNTIL_STALE = 14

@eel.expose
def get_sources():
    js_scrapers = []
    for scraper in scrapers:
        js_scrapers.append((scraper.source_id, scraper.url, scraper.name, scraper.language, scraper.scrape_type, scraper.last_scrape_time.isoformat()))
    js_scrapers = sorted(js_scrapers, key=lambda x: x[2], reverse=True)
    return js_scrapers

@eel.expose
def get_days_until_stale():
    return EMPTY_DAYS_UNTIL_STALE




def InitialiseSources():
    scrapers = []
    constructors = {"Web scraper": NewspaperScraper,
                    "RSS/Atom Feed": FeedScraper}

    for source in GetAllSources(MAX_ACTIVE_SCRAPERS):
        source_id = source["_id"]
        scraper_type = source["_source"]["Data Source"]
        url = source["_source"]["URL"]
        name = source["_source"]["Name"]
        country = source["_source"]["Country"]
        lang = source["_source"]["Language"]
        last_scrape_time = source["_source"]["Last Retrieved"]
        enabled = source["_source"]["Active"]
        try:
            scraper = constructors[scraper_type](url, name, country, lang, source_id, last_scrape_time, enabled)
            scrapers.append(scraper)
        except Exception as e:
            print(str(e))
            continue

    return scrapers

CreateDB()
scrapers = InitialiseSources()
classifier = BERTClassifier("./.ml/", False)

def scrape_sources(id, l, q, scrapers):
    while scrapers:
        begin_time = datetime.now()

        # Go through scraper list
        for i, scraper in enumerate(scrapers):
            if scraper.enabled:
                results = scraper.scrape()
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

        # Classify results and add to db
        with l:
            categories = classifier.classify(results)
            # Add to DB
            

        # Wait minimum time
        time_elapsed = (datetime.now() - begin_time).seconds
        if time_elapsed < MIN_SECONDS_PER_SCRAPE:
            time_remaining = MIN_SECONDS_PER_SCRAPE - time_elapsed
            print(f"[{id}] Sleeping for {time_remaining} seconds...")
            time.sleep(time_remaining)


# Main function
print(f"Beginning to scrape from {len(scrapers)} sources")
# if USE_CONCURRENCY:
#     random.shuffle(scrapers)
#     lock = threading.Lock()
#     # Split sources into threads
#     n = len(scrapers) // NO_WORKERS
#     threads = list()
#     remaining = queue.Queue()
#     # Create queue of newly activated sources
#     for elt in scrapers[n*NO_WORKERS:]:
#         remaining.put(elt)
#     # Start threads
#     for i in range(NO_WORKERS):
#         x = threading.Thread(target=scrape_sources, args=(i, lock, remaining,scrapers[n*i:n*(i+1)]))
#         threads.append(x)
#         x.start()

#     for t in threads:
#         t.join()
# else:
#     # Non-concurrent version
#     while scrapers:
#         for scraper in scrapers:
#             if scraper.enabled:
#                 scraper.scrape()
#             else:
#                 scrapers.pop(scraper)

eel.init('dynamic_interface')
print("Starting web server...")
eel.start('index.html')

# while scrapers:
#     for scraper in scrapers:
#         if scraper.enabled:
#             articles = scraper.scrape()
#             if articles:
#                 categories = classifier.classify(articles)
#                 AddArticles(articles, categories)