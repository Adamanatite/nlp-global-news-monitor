from sources.scraper import Scraper
import newspaper
import re
from elasticsearch_database import GetArticleURL
from langdetect import detect

def cleanup(text):
    #Check if lines has at least one alphanumeric digit (adapted from https://stackoverflow.com/a/6676843)
    return "\n".join([l for l in text.split("\n") if l and bool(re.search('[a-z0-9]', l, re.IGNORECASE))])

class NewspaperScraper(Scraper):

    #Function for newspaper3k to create a parsed article
    def article_parse(self, url):
        if self.language:
            article = newspaper.Article(url,language=self.language)
        else:
            article = newspaper.Article(url)
        article.download()
        article.parse()
        return article

    def __init__(self, url, name=None, country=None, lang=None, source_id=None, last_scraped=None):
        self.scrape_type = "Web scraper"
        super().__init__(url, name, country, lang, source_id, last_scraped)

    def GetNewArticles(self):
        self.scraper = newspaper.build(self.url, language=self.language, fetch_images=False)
        # Get all new articles
        for article in self.scraper.articles:
            # Remove duplicate URL's (with URL parameters)
            if '#' in article.url or '?' in article.url or GetArticleURL(article.url):
                continue

            try:
                # Parse and add
                news = self.article_parse(article.url)
                if news and news.title:
                    lang = detect(news.title)[:2]
                    # Re-parse article if we have chosen the wrong language (for multilignual sources)
                    if not news.text and not lang == self.language:
                        news = self.article_parse(article.url, lang)
                    self.AddNewArticle(news.url, news.title, cleanup(news.text), news.publish_date, language=lang)
            except Exception as e:
                err = str(e)
                # If the URL doesn't work, simply skip the article. Otherwise if there is a connection issue stop scraping until the next loop
                if "404 Client Error" in err or "403 Client Error" in err:
                    continue
                else:
                    break

