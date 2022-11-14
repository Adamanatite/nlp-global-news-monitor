from elasticsearch_database import CreateDB
from sources.newspaper3k_scraper import NewspaperScraper
import time

CreateDB()

with open("sources.txt") as f:
    # Parse source file
    scrapers = []
 
    for line in f:
        data = line.strip().split(" ")
        if len(data) == 1:
            current_lang = data[0]
            continue
        # Create source object
        source = NewspaperScraper(url=data[-5], name=" ".join(data[:-5]), country=data[-4], lang=current_lang)
        scrapers.append(source)

while True:
    for scraper in scrapers:
        scraper.scrape()
    print("Sleeping...\n\n")
    time.sleep(120)