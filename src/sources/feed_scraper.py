import feedparser
from datetime import datetime
from elasticsearch_database import AddArticle, AddSource
from time import mktime

stale_days = 7

class FeedScraper:

    scrape_type = "RSS/Atom Feed"
    #TODO: get all this data from database
    last_scrape_time = datetime(month=1, day=1, year=2000)
    is_stale = False
    enabled = True

    #TODO: Determine when self is stale (last scraped date over a certain threshold)
    def __init__(self, url, name=None, country=None, lang=None, exists=True):
        self.url = url
        #TODO: Determine these parameters from the url (or the database if it already exists)
        self.name = name
        self.language = lang
        self.country = country
        if not exists:
            AddSource(self.url, self.name, self.country, self.language, self.scrape_type)
        print("Initialised " + self.name + " feed")

    def scrape(self):

        if not self.enabled:
            return

        parsed = feedparser.parse(self.url)

        # Adapted from https://stackoverflow.com/a/59615563
        new_items = [entry for entry in parsed.entries if
                datetime.fromtimestamp(mktime(entry.updated_parsed)) > self.last_scrape_time]
        
        if len(new_items) > 0:
            self.is_stale = False
            new_items.sort(reverse=True, key=lambda x: x.updated_parsed)
            self.last_scrape_time = datetime.fromtimestamp(mktime(new_items[0].updated_parsed))
            #TODO: Remove limit of 5
            for item in new_items[:5]:
                if len(item.summary) > 0:
                    AddArticle(item.link, item.title, item.summary, datetime.fromtimestamp(mktime(item.updated_parsed)).strftime("%Y-%m-%dT%H:%M:%SZ"), self.name)
                else:
                    AddArticle(item.link, item.title, None, datetime.fromtimestamp(mktime(item.updated_parsed)).strftime("%Y-%m-%dT%H:%M:%SZ"), self.name)
        else:
            #Set as stale
            if (datetime.now() - self.last_scrape_time).days > stale_days:
                self.is_stale = True
