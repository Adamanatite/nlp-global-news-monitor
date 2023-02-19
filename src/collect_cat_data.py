import newspaper
from database.elasticsearch_database import AddArticle


MIN_ARTICLE_LENGTH = 100

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
                if line.count(".") > 1 and not "www" in line:
                    cat_start = line.find("://")+3
                    cat_end = line.find(".")
                    cat_string = line[cat_start:cat_end]
                    TLD = line[:cat_start] + "www" + line[cat_end:]
                else:
                    line = line[::-1]
                    cat_end = line[1:].find("/")+1
                    cat_string = line[1:cat_end][::-1]
                    TLD = line[cat_end:][::-1]
                np3k_feeds[TLD] = np3k_feeds.get(TLD, {})
                np3k_feeds[TLD][cat_string] = current_cat

        return rss_feeds, np3k_feeds

def build_sources():
    pass

def get_rss_articles(source):
    pass

def get_np3k_articles(source):
    pass

def scrape_details(data):
    titles = set()
    for (url, language, scrape_type, category) in data:
        try:
            # Parse and add
            news = article_parse(url, lang=language)
            if news and news.title and news.text and len(news.text) > MIN_ARTICLE_LENGTH:
                #Validate article is unique
                if news.title in titles:
                    continue
                # Add article
                print(news.title)
                AddArticle(url, news.title, cleanup(news.text), None, language, news.publish_date, None, scrape_type, category)
                titles.add(news.title)
        except Exception as e:
            err = str(e)
            print(err)
            # If the URL doesn't work, simply skip the article. Otherwise if there is a connection issue stop scraping until the next loop
            if "404 Client Error" in err or "403 Client Error" in err:
                continue
            else:
                break

rss_feeds, np3k_feeds = get_sources_from_file()
print(len(rss_feeds))
print(rss_feeds[:10])
print(len(np3k_feeds))
print(list(np3k_feeds.keys())[:10])