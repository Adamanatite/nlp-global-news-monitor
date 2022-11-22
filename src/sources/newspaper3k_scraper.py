import newspaper
import json
import re
from datetime import datetime
import time
from elasticsearch_database import AddArticle, AddSource, UpdateLastScraped

def cleanup(text):
    #Check if lines has at least one alphanumeric digit (adapted from https://stackoverflow.com/a/6676843)
    return "\n".join([l for l in text.split("\n") if l and bool(re.search('[a-z0-9]', l, re.IGNORECASE))])

#Function for newspaper3k to create a parsed article
def article_parse(url,language=None):
    if language:
        article = newspaper.Article(url,language=language)
    else:
        article = newspaper.Article(url)
    article.download()
    article.parse()
    return article

# Get data from JSON file
with open("sources/config.json") as f:
    data = json.load(f)
    try:
        STALE_DAYS = int(data["empty_days_until_stale"])
        FAILURES_UNTIL_DISABLE = int(data["failures_until_disable"])
        AUTO_DISABLE_STALE_SOURCES = bool(data["auto_disable_stale_sources"])
    except:
        # Default values
        STALE_DAYS = 7
        FAILURES_UNTIL_DISABLE = 5
        AUTO_DISABLE_STALE_SOURCES = False

class NewspaperScraper:

    scrape_type = "Web scraper"
    #TODO: get all this data from database
    # Last article scraped and time of last fresh scrape
    last_url = None
    last_scrape_time = datetime(month=1, day=1, year=2000)
    is_stale = False
    enabled = True
    no_consecutive_failures = 0

    def __init__(self, url, name=None, country=None, lang=None, source_id=None, last_scrape_time=None, exists=True):
        self.url = url
        self.source_id = source_id
        #TODO: Determine these parameters from the url (or the database if it already exists)
        self.name = name
        self.language = lang
        self.country = country
        if not exists:
            self.source_id = AddSource(self.url, self.name, self.country, self.language, self.scrape_type)
        if last_scrape_time:
            self.last_scrape_time = datetime(last_scrape_time)
        print("Initialised " + self.name + " scraper")

    def scrape(self):
       
        if not self.enabled:
            return

        self.scraper = newspaper.build(self.url, language=self.language)

        # Get all new articles
        for article in self.scraper.articles:
            # Assumes articles scraped are in date order, newest first (to be proven)
            if article.url == self.last_url:
                break

            # Remove duplicate URL's (with URL parameters)
            if '#' in article.url:
                continue

            try:
                # Parse and add
                news = article_parse(article.url, language=self.language)
                if news and news.title and AddArticle(news.url, news.title, cleanup(news.text), self.country, self.language, news.publish_date, self.name):
                    # Update to reflect new source found
                    self.last_scrape_time = datetime.now()
                    self.is_stale = False
                self.no_consecutive_failures = 0
            except Exception as e:
                print(self.name + " error: " + str(e))
                #TODO: system for re-enabling (in case of internet error etc)
                self.no_consecutive_failures += 1
                if self.no_consecutive_failures > FAILURES_UNTIL_DISABLE:
                    self.enabled = False
                break

            #TODO: Create better rate limiting system
            time.sleep(1)

        #Update last url
        if self.scraper.articles:
            self.last_url = self.scraper.articles[0].url

        #Set as stale
        if (datetime.now() - self.last_scrape_time).days > STALE_DAYS:
            self.is_stale = True
            if AUTO_DISABLE_STALE_SOURCES:
                self.enabled = False

        #Update self
        UpdateLastScraped(self.source_id, self.last_scrape_time)