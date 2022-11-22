from sources.scraper import Scraper
import newspaper
import re
from elasticsearch_database import GetArticle

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

class NewspaperScraper(Scraper):

    def __init__(self, url, name=None, country=None, lang=None, source_id=None, last_scraped=None):
        self.scrape_type = "Web scraper"
        super().__init__(url, name, country, lang, source_id, last_scraped)
        # Build scraper once to add old articles to cache (so we only scrape new ones)
        # self.scraper = newspaper.build(self.url, language=self.language)

    def GetNewArticles(self):
        self.scraper = newspaper.build(self.url, language=self.language)

        # Get all new articles
        for article in self.scraper.articles:

            # Remove duplicate URL's (with URL parameters)
            if '#' in article.url or '?' in article.url or GetArticle(article.url):
                continue

            try:
                # Parse and add
                news = article_parse(article.url, language=self.language)
                if news and news.title:
                    self.AddNewArticle(news.url, news.title, cleanup(news.text), news.publish_date, skip_verification=True)
                self.no_consecutive_failures = 0
            except Exception as e:
                self.HandleError(e)
                break