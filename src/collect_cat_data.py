import newspaper
from database.elasticsearch_database import CreateDB, AddArticle
from datetime import datetime, timedelta
from time import mktime
import feedparser
import time
import re

MIN_ARTICLE_LENGTH = 100
MIN_SECONDS_PER_SCRAPE = 300

last_scrape_time = datetime.now() - timedelta(days=1)


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

def get_sources_from_file():

    rss_feeds = []
    np3k_feeds = {}

    with open("data_collection.txt", encoding="utf-8") as f:
        current_cat = None
        current_lang = None
        for line in f:
            line = line.strip()
            if not line: 
                continue
            if line == "END":
                break

            if line[-1] == ":":
                if len(line) == 3:
                    current_lang = line[:2].lower()
                else:
                    current_cat = line[:-1]
            else:
                if "rss" in line or "xml" in line or "feed" in line:
                    rss_feeds.append((line, current_lang, current_cat))
                    continue
                if not line[-1] == "/":
                    line += "/"
                if line.count("/") < 4:
                    cat_start = line.find("://")+3
                    cat_end = line.find(".")
                    cat_string = line[cat_start:cat_end]
                    TLD = line[:cat_start] + "www" + line[cat_end:] + current_lang
                else:
                    line = line[::-1]
                    cat_end = line[1:].find("/")+1
                    cat_string = line[1:cat_end][::-1]
                    TLD = line[cat_end:][::-1] + current_lang

                np3k_feeds[TLD] = np3k_feeds.get(TLD, {})
                if cat_string in np3k_feeds[TLD]:
                    print(TLD, cat_string)
                np3k_feeds[TLD][cat_string] = current_cat
        return rss_feeds, np3k_feeds

def get_rss_articles(sources): 
    print("Scraping RSS")
    global last_scrape_time
    articles = []
    start_scrape_time = datetime.now()
    for source in sources:
        try:
            parsed = feedparser.parse(source[0])
        except Exception as e:
            print(source[0] + " error: " + str(e))
            continue
        # Adapted from https://stackoverflow.com/a/59615563
        try:
            new_items = [entry for entry in parsed.entries if
                datetime.fromtimestamp(mktime(entry.updated_parsed)) > last_scrape_time]
        # Empty RSS Feeds
        except AttributeError:
            continue

        for item in new_items:
            articles.append((item.link, source[1], "RSS/Atom Feed", source[2]))

    last_scrape_time = start_scrape_time

    scrape_details(articles)
    return articles

def get_np3k_articles(sources):
    print("Scraping Web")
    articles = []
    for source in sources:
        url = source[:-2]
        lang = source[-2:]
        scraper = newspaper.build(url, language=lang, fetch_images=False)

        for article in scraper.articles:
            for cat in sources[source]:
                if "/" + cat + "/" in article.url or cat + "." in article.url or cat + "-" in article.url:
                    articles.append((article.url, lang, "Web Scraper", sources[source][cat]))
    scrape_details(articles)
    return articles


def scrape_details(data):
    titles = set()

    print("Number of articles:", len(data))

    for (url, language, scrape_type, category) in data:
        try:
            # Parse and add
            news = article_parse(url, lang=language)
            if news and news.title and news.text and len(news.text) > MIN_ARTICLE_LENGTH:
                #Validate article is unique
                if news.title in titles:
                    continue
                # Add article
                print(scrape_type, category, news.title)
                AddArticle(url, news.title, cleanup(news.text), None, language, news.publish_date, "Dataset Collection", scrape_type, category)
                titles.add(news.title)
        except Exception as e:
            err = str(e)
            print(err)
            # If the URL doesn't work, simply skip the article. Otherwise if there is a connection issue stop scraping until the next loop
            continue



def collect_data(rss_feeds, np3k_feeds):
    while True:
        begin_time = datetime.now()

        # Go through scraper list
        get_rss_articles(rss_feeds)
        get_np3k_articles(np3k_feeds)

        # Wait minimum time
        time_elapsed = (datetime.now() - begin_time).seconds
        if time_elapsed < MIN_SECONDS_PER_SCRAPE:
            time_remaining = MIN_SECONDS_PER_SCRAPE - time_elapsed
            print(f"[{id}] Sleeping for {time_remaining} seconds...")
            time.sleep(time_remaining)

CreateDB()
rss, np3k = get_sources_from_file()
collect_data(rss, np3k)