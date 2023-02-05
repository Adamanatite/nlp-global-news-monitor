import newspaper

def article_parse(url):
    article = newspaper.Article(url)
    article.download()
    article.parse()
    return article

scraper = newspaper.build("https://www.bbc.co.uk/news/coronavirus")

articles = []
# Get all new articles
for article in scraper.articles:
    # Remove duplicate URL's (with URL parameters)
    try:
        # Parse and add
        news = article_parse(article.url)
        if news and news.title:
            # Add article
            print("BBC Coronavirus: " + news.title)
    except Exception as e:
        continue
print("Done")