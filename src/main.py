from scraper_database import CreateDB, AddArticle, AddSource
from newspaper import Article
import re

def cleanup(text):
    #Check if lines has at least one alphanumeric digit (adapted from https://stackoverflow.com/a/6676843)
    return "\n".join([l for l in text.split("\n") if l and bool(re.search('[a-z0-9]', l, re.IGNORECASE))])

#Function for newspaper3k to create a parsed article
def article_parse(url,language=None):
    if language:
        article = Article(url,language=language)
    else:
        article = Article(url)
    article.download()
    article.parse()
    return article

CreateDB()

AddSource("https://www.bbc.co.uk/news", "BBC News", "UK", "en")

url = "https://www.bbc.co.uk/news/uk-politics-63466532"
test_article = article_parse(url, language="en")
AddArticle(url, test_article.title, cleanup(test_article.text), test_article.publish_date, "https://www.bbc.co.uk/news")

print("Added source and article")