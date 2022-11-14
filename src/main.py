from elasticsearch_database import CreateDB, AddArticle, AddSource
import newspaper
import re
import time

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

CreateDB()

AddSource("https://www.bbc.co.uk/news", "BBC News", "UK", "en")

url = "https://www.bbc.co.uk/news/uk-politics-63466532"
test_article = article_parse(url, language="en")
AddArticle(url, test_article.title, cleanup(test_article.text), test_article.publish_date, "https://www.bbc.co.uk/news")

print("Added source and article")

# with open("sources.txt") as f:
#     # Parse source file
#     sources = []
    
#     current_key = None
#     for line in f:
#         data = line.strip().split(" ")
#         if len(data) == 1:
#             current_lang = data[0]
#             continue
#         # Create tuple (url, name, country, language) and add to list
#         sources.append((data[-5], " ".join(data[:-5]), data[-4], current_lang))

# scrapers = []
# for source in sources[:10]:
#     print(source[0], source[3])
#     scrapers.append(newspaper.build(source[0], language=source[3], memoize_articles=False))
#     # AddSource(source[0], source[1], source[2], source[3])

# for scraper in scrapers:
#     print(scraper.size())