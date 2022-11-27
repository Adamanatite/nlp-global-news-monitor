# From https://codeolives.com/2020/01/10/python-reference-module-in-parent-directory/
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from elasticsearch_database import CreateDB, AddSource

CreateDB()

with open(str(parentdir) + "/data/rss_feeds.txt", encoding="utf8") as f:
    for line in f:
        data = line.strip().split(",")
        # Create source object
        #TODO: Manually do country or workout way to automatically do country
        AddSource(data[1], data[2], data[4], data[3], "RSS/Atom Feed")

with open(str(parentdir) + "/data/sources.txt", encoding="utf8") as f:
    # Parse source file
    scrapers = []

    for line in f:
        data = line.strip().split(" ")
        if len(data) == 1:
            current_lang = data[0]
            continue
        # Create source object
        AddSource(data[-5], " ".join(data[:-5]), data[-4], current_lang, "Web scraper")