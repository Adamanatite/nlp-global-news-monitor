from database.database_connector import CreateDB, GetAllSources, AddArticles
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

# For managing shared access to the scraper list from this program and the web interface
lock = threading.Lock()

# Global variable for enabling/disabling the scraper system
isSystemEnabled = False

@eel.expose
def get_sources():
    js_scrapers = []
    with lock:
        for scraper in scrapers:
            js_scrapers.append((scraper.source_id, scraper.url, scraper.name, scraper.language, scraper.scrape_type, scraper.last_scrape_time.isoformat(), scraper.enabled))
    js_scrapers = sorted(js_scrapers, key=lambda x: x[2], reverse=True)
    return js_scrapers

@eel.expose
def get_days_until_stale():
    return EMPTY_DAYS_UNTIL_STALE

@eel.expose
def toggle_source(source_id):
    with lock:
        for scraper in scrapers:
            if source_id == scraper.source_id:
                scraper.toggle()
                return True
    return False

@eel.expose
def delete_source(source_id):
    with lock:
        for i, scraper in enumerate(scrapers):
            if source_id == scraper.source_id:
                scraper.delete()
                scrapers.pop(i)
                return True
    return False

@eel.expose
def is_system_enabled():
    return isSystemEnabled

@eel.expose
def toggle_system():
    global isSystemEnabled
    isSystemEnabled = not isSystemEnabled
    return isSystemEnabled

@eel.expose
def add_source(url, source_name, language, country, source_type):
    constructors = {"Web crawler": NewspaperScraper,
                    "RSS/Atom feed": FeedScraper}
    if language == "Unknown":
        language = None
    new_scraper = constructors[source_type](url, source_name, country, language)
    with lock:
        scrapers.append(new_scraper)
    return new_scraper.source_id, new_scraper.url, new_scraper.name, new_scraper.language, new_scraper.scrape_type, new_scraper.last_scrape_time.isoformat(), True



def scrape_sources(scrapers, classifier):
    while True:
        for scraper in scrapers:
            # Check for web server stoppage
            if event.is_set():
                return
            # Block until system is re-enabled
            if not isSystemEnabled:
                while not isSystemEnabled:
                    if event.is_set():
                        return
                    continue
            # Check for disabled system
            if scraper.enabled:
                articles = scraper.scrape()
                if articles:
                    categories = classifier.classify(articles)
                    AddArticles(articles, categories)

def initialise_sources():
    scrapers = []
    constructors = {"Web crawler": NewspaperCrawler,
                    "RSS/Atom feed": FeedCrawler}

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
# Initialise scraper list and classifier
scrapers = initialise_sources()
classifier = BERTClassifier("./.ml/", False)

# Start scraping system and web server
eel.init('web_interface')
event = threading.Event()
t = threading.Thread(target=scrape_sources, args=(scrapers,classifier))
print("Starting scraper system...")
t.start()
print("Starting web server...")
eel.start('index.html')
print("\n\nWeb server stopped.")
event.set()
t.join()
print("Scraping system stopped.")
