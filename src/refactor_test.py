from crawlers.feed_crawler import FeedCrawler
from crawlers.newspaper3k_crawler import NewspaperCrawler
from parsers.article_parser import ArticleParser
from classifier.random_classifier import RandomClassifier
from database.database_connector import create_db
import threading

def scrape_sources(crawlers, pipelines):
    """
    Scrapes the websites using the crawlers and runs through the
    article parsing and classification pipeline, until interrupted

    :param crawlers: The source crawlers to collect data using
    :param pipelines: The source to parser/classifier pipelines in use
    """
    # Initialise article lists
    pipeline_articles = [[] for i in range(len(pipelines))]
    # Run infinite loop
    while True:
        for crawler in crawlers:
            # Get articles
            articles = crawler.crawl()
            # Assign articles to pipeline(s)
            if articles:
                for i, pipeline in enumerate(pipelines):
                    source_types = pipeline[0]
                    if crawler.source_type == source_types or (isinstance(source_types, list) and crawler.source_type in source_types):
                        print("Adding " + crawler.source_type + " to pipeline " + str(i))
                        pipeline_articles[i].extend(articles)

        # Parse and classify articles
        for i, pipeline in enumerate(pipelines):
            pipeline_parser = pipeline[1]
            pipeline_parser.parse(pipeline_articles[i])
            pipeline_articles[i] = []


create_db()

np3k_crawler = NewspaperCrawler("https://www.bbc.co.uk/news", "BBC News", "GB", "en")
rss_crawler = FeedCrawler("https://www.bbc.com/mundo/ultimas_noticias/index.xml", "BBC News; World", "GB", "es")

np3k_articles = np3k_crawler.crawl()
rss_articles = rss_crawler.crawl()

categories = ["Arts/Entertainment", "Sports", "Politics", "Science/Technology", "Business/Finance", "Health/Welfare"]
classifier = RandomClassifier(categories)
lock = threading.Lock()
parser = ArticleParser(classifier, lock)

crawlers = [np3k_crawler, rss_crawler]

"""
Pipelines
"""
pipelines = [(["Web crawler", "RSS/Atom feed"], parser),
             ("RSS/Atom feed", parser),
             ("Web crawler", parser) ]

scrape_sources(crawlers, pipelines)


