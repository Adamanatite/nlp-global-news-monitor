from scrapers.scraper import Scraper
import feedparser
from datetime import datetime
from time import mktime
from langdetect import detect
import re

def cleanup(text):
    # Remove HTML tags (from https://medium.com/@jorlugaqui/how-to-strip-html-tags-from-a-string-in-python-7cb81a2bbf44)
    tags = re.compile('<.*?>')
    text = re.sub(tags, '', text)
    # Remove multiple spaces, tabs, and newlines
    text = re.sub("( +) | (\t+)", " ", text)
    text = re.sub("(\s|\t)*\n", "\n", text)
    text = re.sub("\n(\n|\s|\t)*", "\n", text)
    return text.strip()

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
                    lang = detect(d.entries[0].title)[:2]
            else:
                lang = lang[:2]

        super().__init__(url, name, country, lang, source_id, last_scraped)

    def GetNewArticles(self):
        articles = []
        try:
            parsed = feedparser.parse(self.url)
        except Exception as e:
            print(self.name + " error: " + str(e))
            return []
        # Adapted from https://stackoverflow.com/a/59615563
        try:
            new_items = [entry for entry in parsed.entries if
                    datetime.fromtimestamp(mktime(entry.updated_parsed)) > self.last_scrape_time]
        except:
            print("No updated date:", parsed.entries[0])
            return []

        if len(new_items) > 0:
            new_items.sort(reverse=True, key=lambda x: x.updated_parsed)
            for item in new_items:
                print(self.name + ": " + item.title)
                articles.append((item.link, item.title, cleanup(item.summary), self.country, self.language, datetime.fromtimestamp(mktime(item.updated_parsed)), self.name, self.scrape_type))
            self.last_scrape_time = datetime.fromtimestamp(mktime(new_items[0].updated_parsed))
        return articles
        
