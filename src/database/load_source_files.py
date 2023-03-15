from elasticsearch_database import CreateDB, AddSource
import os
# Get current directory from project tree
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
this_dir = str(parentdir) + "/database/"

CreateDB()

with open(this_dir + "data/rss_feeds.txt", encoding="utf8") as f:
    for line in f:
        data = line.strip().split(",")
        # Create source object
        AddSource(data[1], data[2], data[4], data[3], "RSS/Atom feed")

with open(this_dir + "data/sources.txt", encoding="utf8") as f:
    # Parse source file
    scrapers = []

    for line in f:
        data = line.strip().split(" ")
        if len(data) == 1:
            current_lang = data[0]
            continue
        # Create source object
        AddSource(data[-5], " ".join(data[:-5]), data[-4], current_lang, "Web scraper")