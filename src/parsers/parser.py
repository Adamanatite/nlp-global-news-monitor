import os
import re
import json
from datetime import datetime, timezone
from database.database_connector import add_source, update_last_scraped, enable_source, disable_source, delete_source, get_article_from_url
from utils.parse_config import ParseBoolean


# Get current directory from project tree
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

# Get data from JSON file
with open(str(parentdir) + "/config.json", encoding="utf-8") as f:
    data = json.load(f)
    try:
        MIN_ARTICLE_LENGTH = int(data["min_article_length"])
    except:
        # Default values
        print("Error in config")
        MIN_ARTICLE_LENGTH = 300


class Parser:
    """
    Abstract class for parsing a list of given URLs with source details
    """
    def __init__(self, classifier, lock):
        """
        Initialises parameters, attempting to guess country if it is not specified.
        If not given a source ID, it will create the source object in the database 
        and use its new ID
        """
        # Update parameters
        self.classifier = classifier
        self.lock = lock
        self.min_article_length = MIN_ARTICLE_LENGTH


    def update_times(self, time_updates):
        """
        Updates the last scrape time of all crawlers which retrieved new articles
        """
        with self.lock:
            for update in time_updates:
                crawler = update[0]
                time = update[1]
                crawler.set_last_scrape_time(time)


    def parse(self, urls):
        """
        Parses the given list of URLs, which contain information on the source
        and feeds the output to the classifier
        (language, country, source, source type and reference to the crawler)
        """ 
        parsed_data = self.get_parsed_urls(urls)
        self.classifier.classify(parsed_data)


    def get_parsed_urls(self, urls):
        """
        To be overriden in subclasses by a method which 
        scrapes a list of URLs for the webpage content
        """  
        return []


