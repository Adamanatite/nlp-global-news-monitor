import newspaper
import re
from database.elasticsearch_database import AddArticle, UpdateLastScraped
from langdetect import detect
from datetime import timezone

# TODO: Get this from config
MIN_ARTICLE_LENGTH = 300

def cleanup(text):
    #Check if lines has at least one alphanumeric digit (adapted from https://stackoverflow.com/a/6676843)
    return "\n".join([l for l in text.split("\n") if l and bool(re.search('[a-z0-9]', l, re.IGNORECASE))])

#Function for newspaper3k to create a parsed article
def article_parse(url, lang=None):
    if lang:
        article = newspaper.Article(url,language=lang)
    else:
        article = newspaper.Article(url)

    article.download()
    article.parse()
    return article

def parse(articles):

    new_source_publish_dates = {}

    titles = []
    parsed_articles = []
    for article in articles:
        try:
            # Parse and add
            news = article_parse(article["url"], lang=article["language"])
            if news and news.title:
                #Validate article is unique
                if news.title in titles:
                    continue
                # Re-parse article if we have chosen the wrong language (for multilignual sources)
                lang = detect(news.title)[:2]
                if not news.text and not lang == article["language"]:
                    news = article_parse(article.url, lang)
                # Remove articles that are too short
                if  not news.text or len(news.text) < MIN_ARTICLE_LENGTH:
                    continue
                #Update publish date
                if "date" not in article:
                    article["date"] = news.publish_date
                # Add article
                parsed_articles.append({
                    "url": article["url"],
                    "title": news.title,
                    "body": cleanup(news.text),
                    "language": article["language"],
                    "country": article["country"],
                    "date": news.publish_date,
                    "source": article["source"],
                    "scraper_type": article["scraper_type"]
                    })
                titles.append(news.title)
        except Exception as e:
            err = str(e)
            print(err)
            # If the URL doesn't work, simply skip the article. Otherwise if there is a connection issue stop scraping until the next loop
            if "404 Client Error" in err or "403 Client Error" in err:
                continue
            else:
                break
    
    for src, time in new_source_publish_dates.items():
        # Convert to UTC
        UpdateLastScraped(src, time.astimezone(timezone.utc))

    return parsed_articles