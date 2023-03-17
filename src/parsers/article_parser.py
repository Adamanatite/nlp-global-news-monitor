from parsers.parser import Parser
import newspaper
import re
from langdetect import detect

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


class ArticleParser(Parser):

    def __init__(self, classifier, lock):
        """
        Initialises the article parser by callling the abstract constructor
        """
        super().__init__(classifier, lock
                         )
def get_parsed_urls(articles):
    """
    Parses the given list of article URLs and returns a parsed list of articles

    :param articles: The list of articles URLs to add
    :returns: The list of parsed articles
    """
    new_source_publish_dates = [])

    titles = []
    parsed_articles = []

    for article in articles:
        try:
            # Parse and add
            news = article_parse(article["url"], lang=article["language"])

            # Ensure article has content
            if news and news.title:
                #Validate article is unique
                if news.title in titles:
                    continue
                # Stop duplicates
                titles.append(news.title)

                # Re-parse article if we have chosen the wrong language (for multilingual sources)
                lang = detect(news.title)[:2]
                if not news.text and not lang == article["language"]:
                    news = article_parse(article.url, lang)

                # Remove articles that are too short
                if  not news.text or len(news.text) < self.min_article_length:
                    continue

                # Add publish date update
                if news.publish_date:
                    new_source_publish_dates.append((article["crawler"], news.publish_date))

                # Add structured article
                parsed_articles.append({
                    "url": article["url"],
                    "title": news.title,
                    "text": cleanup(news.text),
                    "lang": article["language"],
                    "country": article["country"],
                    "date": news.publish_date,
                    "source": article["source"],
                    "source_type": article["source_type"]
                    })
        # Move past failed parse
        except Exception as ex:
            continue

    # Update scraper times
    self.update_times(new_source_publish_dates)

    # Return final parsed list
    return parsed_articles