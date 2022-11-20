from elasticsearch import Elasticsearch
from datetime import datetime
import json

MAX_ACTIVE_SCRAPERS = 1000

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

# Create indices
def CreateDB():

    if not es:
        print("Couldn't connect to elasticsearch")
        return

    # Create source index
    source_mappings = {
            "properties": {
                "URL": {"type": "keyword"},
                "Name": {"type": "text"},
                "Country": {"type": "keyword"},
                "Language": {"type": "keyword"},
                "Data Source": {"type": "keyword"},
                "Active": {"type": "boolean"}
        }
    }

    if not es.indices.exists(index="sources"):
        es.indices.create(index="sources", mappings=source_mappings)
        print("Created sources index")

    # Create article index
    article_mappings = {
            "properties": {
                "URL": {"type": "keyword"},
                "Headline": {"type": "text", "analyzer": "standard"},
                "Body": {"type": "text", "analyzer": "standard"},
                "Published": {"type": "date"},
                "Retrieved": {"type": "date"},
                "Source": {"type": "keyword"}
        }
    }

    if not es.indices.exists(index="articles"):
        es.indices.create(index="articles", mappings=article_mappings)
        print("Created articles index")

def AddSource(url, name, country, lang, scraper_type, index=None):

    if not es:
        return

    doc = {
        "URL": url,
        "Name": name,
        "Country": country,
        "Language": lang,
        "Data Source": scraper_type,
        "Active": True
    }

    try:
        if index:
            res = es.index(index="sources", id=index, document=doc)
        else:
            res = es.index(index="sources", document=doc)
        print("Added source " + name)
        return res
    except Exception as e:
        print(str(e))
        return None

def AddArticle(url, title, text, date, source, index=None):
    
    if not es:
        return

    doc = {
        "URL": url,
        "Headline": title,
        "Body": text,
        "Published": date,
        "Retrieved": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Source": source
    }

    try:
        if index:
            res = es.index(index="articles", id=index, document=doc)
        else:
            res = es.index(index="articles", document=doc)
        print(source + " added article " + title)
        return res
    except Exception as e:
        print(str(e))
        return None

#TODO
def GetSource(url):

    query_body = {
        "query": {
            "term": {
                "URL": {
                    "value": url
                }
            }
        }
    }

    results = es.search(index="sources", body=query_body)

    if results["hits"]["hits"]:
        return results["hits"]["hits"][0]
    return None

def GetActiveSources():

    query_body = {
        "size": MAX_ACTIVE_SCRAPERS,
        "query": {
            "match": {
                "Active": True
            }
        }
    }

    results = es.search(index="sources", body=query_body)

    if results["hits"]["hits"]:
        return results["hits"]["hits"]
    return None

def GetNewestArticle(source):
    pass



# Delete all indices (Reset DB)
def ResetDB():

    if not es:
        print("Couldn't connect to elasticsearch")
        return

    es.options(ignore_status=[400,404]).indices.delete(index='sources')
    es.options(ignore_status=[400,404]).indices.delete(index='articles')