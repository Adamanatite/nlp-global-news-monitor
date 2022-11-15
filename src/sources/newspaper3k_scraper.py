import newspaper
import re
from datetime import datetime
import time
from elasticsearch_database import AddArticle, AddSource

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

stale_days = 7

class NewspaperScraper:

    scrape_type = "Web scraper"
    #TODO: get all this data from database
    # Last article scraped and time of last fresh scrape
    last_url = None
    last_scrape_time = None
    is_stale = False
    enabled = True

    #TODO: Determine when self is stale (last scraped date over a certain threshold)
    def __init__(self, url, name=None, country=None, lang=None):
        self.url = url
        #TODO: Determine these parameters from the url (or the database if it already exists)
        self.name = name
        self.language = lang
        self.country = country
        try:
            self.scraper = newspaper.build(self.url, language=self.language)
        except Exception as e:
            print("Cannot add source " + url)
        else:
            AddSource(self.url, self.name, self.country, self.language, self.scrape_type)
            print("Initialised " + self.name + " scraper")

    def scrape(self):
        new_articles = False

        # Get all new articles
        #TODO: remove limit of 2
        for article in self.scraper.articles[:2]:
            if article.url == self.last_url:
                break
            try:
                # Parse and add
                news = article_parse(article.url, language="en")
                if news and news.title:
                    AddArticle(news.url, news.title, cleanup(news.text), news.publish_date, self.name)
                    # Update to reflect new source found
                    self.last_scrape_time = datetime.now()
                    self.is_stale = False
                    new_articles = True

            except Exception as e:
                print(self.name + " error: " + str(e))
                #TODO: system for re-enabling (in case of internet error etc)
                self.enabled = False
                break

            #TODO: Create better rate limiting system
            time.sleep(2)

        #Update last url
        if self.scraper.articles:
            self.last_url = self.scraper.articles[0].url

        #Set as stale
        if self.last_scrape_time and (not new_articles) and (datetime.now() - self.last_scrape_time).days > stale_days:
            self.is_stale = True