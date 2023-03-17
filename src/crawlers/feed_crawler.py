from crawlers.crawler import Crawler
import feedparser
from datetime import datetime
from time import mktime
from langdetect import detect

class FeedCrawler(Crawler):
    """
    Concrete crawler implementation for retrieving data from RSS or Atom feeds
    """
    def __init__(self, url, name, country=None, lang=None, source_id=None, last_scraped=None, is_active=True):     
        """
        Initialises the RSS feed crawler

        :param url: The source URL
        :param name: The source name
        :param country: The origin country of the source (default is None)
        :param lang: The primary language of the source (default is None)
        :param source_id: The ID of the source (default is None)
        :param last_scraped: The time of the last new URL(default is None)
        :param is_active: If this source is currently active (default is True)
        """

        # Set source type
        self.source_type = "RSS/Atom feed"

        # Try to determine name and language from feed details
        if not lang:
            d = feedparser.parse(url)
            lang= d.get("language", None)
            if not lang:
                if d.entries:
                    lang = detect(d.entries[0].title)[:2]
            else:
                lang = lang[:2]

        # Call abstract constructor
        super().__init__(url, name, country, lang.upper(), source_id, last_scraped, is_active)


    def get_new_articles(self):
        """
        Collects a list of (possibly) new article URLs from the source URL
        :returns: The list of new URLs
        """
        articles = []
        try:
            parsed = feedparser.parse(self.url)
        except Exception as ex:
            print(self.name + " error: " + str(ex))
            return []
        # Adapted from https://stackoverflow.com/a/59615563
        # Add all new articles, or all articles if we can't tell which are new
        try:
            articles = [entry.link for entry in parsed.entries if
                    datetime.fromtimestamp(mktime(entry.updated_parsed)) > self.last_scrape_time]
        except:
            articles = [entry.link for entry in parsed.entries]

        return articles
