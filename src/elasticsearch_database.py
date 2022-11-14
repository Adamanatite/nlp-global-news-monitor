from elasticsearch import Elasticsearch
from datetime import datetime
import json

# Return es connection, or None if it failed
def ESConnect():

    # Get data from JSON file
    with open("db_info.json") as f:
        data = json.load(f)

    ELASTIC_USERNAME = data["username"]
    ELASTIC_PASSWORD = data["password"]
    CERT_PATH = data["cert_path"]

    # Connect to database (adapted from https://www.elastic.co/guide/en/elasticsearch/client/python-api/master/connecting.html)
    try:
        es = Elasticsearch(
        "https://localhost:9200",
        ca_certs=CERT_PATH,
        basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
        )
    except Exception as e:
        print(str(e))
        return None

    # From https://stackoverflow.com/a/31644507
    if not es.ping():
        return None

    return es

# Get DB connection instance
es = ESConnect()

# Code is adapted from https://dylancastillo.co/elasticsearch-python/

# Create indexes
def CreateDB():

    if not es:
        print("Couldn't connect to elasticsearch")
        return

    # Create source index
    source_mappings = {
            "properties": {
                "url": {"type": "text"},
                "name": {"type": "text"},
                "country": {"type": "text"},
                "language": {"type": "text"},
                "active": {"type": "boolean"}
        }
    }

    if not es.indices.exists(index="sources"):
        es.indices.create(index="sources", mappings=source_mappings)
        print("Created sources index")

    # Create article index
    article_mappings = {
            "properties": {
                "url": {"type": "text"},
                "title": {"type": "text", "analyzer": "standard"},
                "text": {"type": "text", "analyzer": "standard"},
                "publish_date": {"type": "text"},
                "scrape_date": {"type": "text"},
                "source": {"type": "text"}
        }
    }

    if not es.indices.exists(index="articles"):
        es.indices.create(index="articles", mappings=article_mappings)
        print("Created articles index")

def AddSource(url, name, country, lang, scraper_type, index=None):

    if not es:
        return

    doc = {
        "url": url,
        "name": name,
        "country": country,
        "language": lang,
        "scraper_type": scraper_type,
        "active": True
    }

    try:
        if index:
            es.index(index="sources", id=index, document=doc)
        else:
            es.index(index="sources", document=doc)
        print("Added source " + name)
        return True
    except Exception as e:
        print(str(e))
        return False

def AddArticle(url, title, text, date, source, index=None):
    
    if not es:
        return

    doc = {
        "url": url,
        "title": title,
        "text": text,
        "publish_date": date,
        "scrape_date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "source": source
    }

    try:
        if index:
            es.index(index="articles", id=index, document=doc)
        else:
            es.index(index="articles", document=doc)
        print("Added article " + title)
        return True
    except Exception as e:
        print(str(e))
        return False

# Delete all indices (Reset DB)
def ResetDB():

    if not es:
        print("Couldn't connect to elasticsearch")
        return

    es.options(ignore_status=[400,404]).indices.delete(index='sources')
    es.options(ignore_status=[400,404]).indices.delete(index='articles')