from sources.scraper import Scraper
import feedparser
from datetime import datetime
from time import mktime
from langdetect import detect


class FeedScraper(Scraper):

    def __init__(self, url, name=None, country=None, lang=None, source_id=None, last_scraped=None):
        self.scrape_type = "RSS/Atom Feed"
        
        # Try to determine name and language from feed details
        if not name or not lang:
            d = feedparser.parse(url)

        if not name:
            name= d.get("title", None)
        if not lang:
            lang= d.get("language", None)
            if not lang:
                if d.entries:
                    lang = detect(self.entries[0].title)[:2]
            else:
                lang = lang[:2]

        super().__init__(url, name, country, lang, source_id, last_scraped)

    def GetNewArticles(self):
        try:
            parsed = feedparser.parse(self.url)
            self.no_consecutive_failures = 0
        except Exception as e:
            print(self.name + " error: " + str(e))
            return
        # Adapted from https://stackoverflow.com/a/59615563
        new_items = [entry for entry in parsed.entries if
                datetime.fromtimestamp(mktime(entry.updated_parsed)) > self.last_scrape_time]

        if len(new_items) > 0:
            new_items.sort(reverse=True, key=lambda x: x.updated_parsed)
            for item in new_items:
                self.AddNewArticle(item.link, item.title, item.summary, datetime.fromtimestamp(mktime(item.updated_parsed)),update_time=False,skip_verification=True)
            self.last_scrape_time = datetime.fromtimestamp(mktime(new_items[0].updated_parsed))
                
        
