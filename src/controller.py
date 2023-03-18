import threading
import json
import time
from datetime import datetime
import eel
from database.database_connector import create_db, get_sources
from crawlers.newspaper3k_crawler import NewspaperCrawler
from crawlers.feed_crawler import FeedCrawler
from parsers.article_parser import ArticleParser
from classifier.random_classifier import RandomClassifier


def parse_boolean(s):
    """
    Parses a boolean string from the config

    :param s: The boolean string
    :returns: A boolean which represents the string
    """
    return s.lower() == "true"

# Get config data
with open("config.json", encoding="utf-8") as f:
    data = json.load(f)
    try: 
        MIN_SECONDS_PER_SCRAPE = int(data["min_seconds_per_scrape"])
        MAX_ACTIVE_CRAWLERS = int(data["max_active_crawlers"])
        EMPTY_DAYS_UNTIL_STALE = int(data["empty_days_until_stale"])
        AUTO_DISABLE_STALE_SOURCES = parse_boolean(data["auto_disable_stale_sources"])
    except Exception as e:
        print("Error in config.json file")
        MIN_SECONDS_PER_SCRAPE = 600
        MAX_ACTIVE_CRAWLERS = 1000
        EMPTY_DAYS_UNTIL_STALE = 14
        AUTO_DISABLE_STALE_SOURCES = False

# Crawler constructors by name (for loading from DB)
constructors = {"Web crawler": NewspaperCrawler,
                "RSS/Atom feed": FeedCrawler}
# For managing shared access to the crawler list from this program, the parser and the web interface
lock = threading.Lock()
# Global variable for enabling/disabling the crawler system
is_system_enabled = False


# Web connector functionality


@eel.expose
def get_js_sources():
    """
    Sends a list of formatted sources to the web interface

    :returns: A list of formatted sources
    """
    js_crawlers = []
    with lock:
        for crawler in crawlers:
            js_crawlers.append((crawler.source_id, crawler.url, crawler.name, crawler.language, crawler.source_type, crawler.last_scrape_time.isoformat(), crawler.enabled))
    js_crawlers = sorted(js_crawlers, key=lambda x: x[2], reverse=True)
    return js_crawlers

@eel.expose
def get_days_until_stale():
    """
    Sends the days until a source is stale to the web interface

    :returns: The days until a source is stale (from config)
    """
    return EMPTY_DAYS_UNTIL_STALE

@eel.expose
def toggle_source(source_id):
    """
    Toggles the source with a given source ID

    :param source_id: The source ID
    :returns: A boolean which represents whether the operation was successful
    """
    with lock:
        for crawler in crawlers:
            if source_id == crawler.source_id:
                crawler.toggle()
                return True
    return False

@eel.expose
def delete_source(source_id):
    """
    Deletes the source with a given source ID

    :param source_id: The source ID
    :returns: A boolean which represents whether the operation was successful
    """
    with lock:
        for i, crawler in enumerate(crawlers):
            if source_id == crawler.source_id:
                crawler.delete()
                crawlers.pop(i)
                return True
    return False

@eel.expose
def get_system_status():
    """
    Returns whether the system is enabled to the web interface

    :returns: Whether the system is enabled
    """
    return is_system_enabled

@eel.expose
def toggle_system():
    """
    Toggles whether the scraper system is enabled

    :returns: The new system state
    """
    global is_system_enabled
    is_system_enabled = not is_system_enabled
    return is_system_enabled

@eel.expose
def add_source(url, source_name, language, country, source_type):
    """
    Adds a source to the database from the web server and returns its details

    :returns: The details of the new source
    """
    if language == "Unknown":
        language = None
    new_crawler = constructors[source_type](url, source_name, country, language, days_until_stale=EMPTY_DAYS_UNTIL_STALE, auto_disable_stale=AUTO_DISABLE_STALE_SOURCES)
    with lock:
        crawlers.append(new_crawler)
    return new_crawler.source_id, new_crawler.url, new_crawler.name, new_crawler.language, new_crawler.source_type, new_crawler.last_scrape_time.isoformat(), True


# Scraper functoinality


def scrape_sources(crawlers, pipelines):
    """
    Scrapes the websites using the crawlers and runs through the
    article parsing and classification pipeline, until interrupted

    :param crawlers: The source crawlers to collect data using
    :param pipelines: The source to parser/classifier pipelines in use
    """
    # Initialise article lists
    pipeline_articles = [[] for i in range(len(pipelines))]
    # Run infinite loop
    while True:
        start_time = datetime.now()
        for crawler in crawlers:
            # Check if thread is stopped
            if event.is_set():
                return
            # Block until system is re-enabled or thread is stopped
            if not is_system_enabled:
                while not is_system_enabled:
                    if event.is_set():
                        return
                    continue

            # Get articles
            articles = crawler.crawl()
            # Assign articles to pipeline
            if articles:
                for i, pipeline in enumerate(pipelines):
                    source_types = pipeline[0]
                    if crawler.source_type == source_types or (isinstance(source_types, list) and crawler.source_type in source_types):
                        pipeline_articles[i].extend(articles)
                        break

        # Parse and classify articles
        for i, pipeline in enumerate(pipelines):
            pipeline_parser = pipeline[1]
            pipeline_parser.parse(pipeline_articles[i])
            pipeline_articles[i] = []

        # Sleep until next scrape
        time_elapsed = (datetime.now() - start_time).total_seconds()
        time_left = MIN_SECONDS_PER_SCRAPE - time_elapsed
        if time_left > 0:
            time.sleep(time_left)

        # Check if thread is stopped
        if event.is_set():
            return


def initialise_sources():
    """
    Initialises the sources from the database

    :returns: A list of crawler objects loaded from the database
    """
    crawlers = []

    for source in get_sources(MAX_ACTIVE_CRAWLERS):
        source_id = source["_id"]
        source_type = source["_source"]["Source Type"]
        url = source["_source"]["URL"]
        name = source["_source"]["Name"]
        country = source["_source"]["Country"]
        lang = source["_source"]["Language"]
        last_scrape_time = source["_source"]["Last Retrieved"]
        enabled = source["_source"]["Active"]
        try:
            crawler = constructors[source_type](url, name, country, lang, source_id, last_scrape_time, enabled, EMPTY_DAYS_UNTIL_STALE, AUTO_DISABLE_STALE_SOURCES)
            crawlers.append(crawler)
        except Exception as ex:
            print(str(ex))
            continue

    return crawlers

# Emsure database exists
create_db()
# Initialise scraper list, parser and classifier
crawlers = initialise_sources()
categories = ["Arts/Entertainment", "Sports", "Politics", "Science/Technology", "Business/Finance", "Health/Welfare"]
classifier = RandomClassifier(categories)
parser = ArticleParser(classifier, lock)


"""
Pipelines
"""
pipelines = [(["Web crawler", "RSS/Atom feed"], parser)]


# Start scraping system and web server
eel.init('web_interface')
event = threading.Event()
t = threading.Thread(target=scrape_sources, args=(crawlers,pipelines))
print("Starting scraper system...")
t.start()
print("Starting web server...")
eel.start('index.html')
print("\n\nWeb server stopped.")
event.set()
t.join()
print("Scraping system stopped.")