import newspaper
from crawlers.crawler import Crawler

class NewspaperCrawler(Crawler):
    """
    Concrete crawler implementation for retrieving data from news websites
    """
    def __init__(self, url, name=None, country=None, lang=None, source_id=None, last_scraped=None, is_active=True, days_until_stale = 14, auto_disable_stale = False):
        """
        Initialises the webpage crawler

        :param url: The source URL
        :param name: The source name
        :param country: The origin country of the source (default is None)
        :param lang: The primary language of the source (default is None)
        :param source_id: The ID of the source (default is None)
        :param last_scraped: The time of the last new URL(default is None)
        :param is_active: If this source is currently active (default is True)
        """

        # Set source type and call abstract constructor
        self.source_type = "Web scraper"
        super().__init__(url, name, country, lang, source_id, last_scraped, is_active, days_until_stale, auto_disable_stale)

    def get_new_articles(self):
        """
        Collects a list of (possibly) new article URLs from the source URL
        :returns: The list of new URLs
        """
        # Get all new articles and return
        crawler = newspaper.build(self.url, language=self.language, fetch_images=False)
        articles = []
        for article in crawler.articles:
            if "#" not in article.url and "?" not in article.url:
                articles.append(article.url)
        return articles
