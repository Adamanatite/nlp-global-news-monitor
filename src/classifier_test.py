from crawlers.feed_crawler import FeedCrawler
from crawlers.newspaper3k_crawler import NewspaperCrawler
from parsers.article_parser import ArticleParser
from classifier.bert_classifier import BERTClassifier
from database.database_connector import create_db
import threading

create_db()

np3k_crawler = NewspaperCrawler("https://www.bbc.co.uk/news", "BBC News", "GB", "en")
rss_crawler = FeedCrawler("https://www.bbc.com/mundo/ultimas_noticias/index.xml", "BBC News; World", "GB", "es")

np3k_articles = np3k_crawler.crawl()
rss_articles = rss_crawler.crawl()


lock = threading.Lock()
classifier = BERTClassifier("./.ml/", "xlm-roberta-base")
parser = ArticleParser(classifier, lock)

parser.parse(np3k_articles + rss_articles)
print("Done!")
