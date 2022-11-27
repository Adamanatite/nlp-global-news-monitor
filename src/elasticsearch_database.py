from elasticsearch import Elasticsearch
from datetime import datetime
import json

# Get data from JSON file
with open("data/config.json") as f:
    conf = json.load(f)

MAX_ACTIVE_SCRAPERS = int(conf["max_active_scrapers"])

# Return es connection, or None if it failed
def ESConnect():

    # Get data from JSON file
    with open("data/db_info.json") as f:
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
                "Last Retrieved": {"type": "date"},
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
                "Headline": {"type": "keyword"},
                "Body": {"type": "keyword"},
                "Country": {"type": "keyword"},
                "Language": {"type": "keyword"},
                "Published": {"type": "date"},
                "Retrieved": {"type": "date"},
                "Source": {"type": "keyword"},
                "Data Source": {"type": "keyword"},
                "Category": {"type": "keyword"}
        }
    }

    if not es.indices.exists(index="articles"):
        es.indices.create(index="articles", mappings=article_mappings)
        print("Created articles index")

def AddSource(url, name, country, lang, scraper_type):

    if not es:
        return

    doc = {
        "URL": url,
        "Name": name,
        "Country": country,
        "Language": lang,
        "Data Source": scraper_type,
        "Last Retrieved": None,
        "Active": True
    }

    try:
        if not GetSource(url):
            res = es.index(index="sources", document=doc)
            print("Added source " + name)
            return res["_id"]
        return None
    except Exception as e:
        print("Couldn't add source " + name)
        return None


def AddArticle(url, title, text, country, lang, date, source, scraper, skip_verification=False):
    
    if not es:
        return

    doc = {
        "URL": url,
        "Headline": title,
        "Body": text,
        "Country": country,
        "Language": lang,       
        "Published": date,
        "Retrieved": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Source": source,
        "Data Source": scraper,
        "Category": "Unknown"
    }

    try:
        if skip_verification or not GetArticle(title,source):
            res = es.index(index="articles", document=doc)
            print(source + " added article " + title)
            return res["_id"]
        return None
    except Exception as e:
        print(source + " couldn't add article " + title)
        print(str(e))
        return None


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

def GetActiveSources(value=True):

    query_body = {
        "size": MAX_ACTIVE_SCRAPERS,
        "query": {
            "match": {
                "Active": value
            }
        }
    }

    results = es.search(index="sources", body=query_body)

    if results["hits"]["hits"]:
        return results["hits"]["hits"]
    return None

def GetArticleURL(url):
    query_body = {
        "query": {
            "term": {
                "URL": {
                    "value": url
                }
            }
        }
    }

    results = es.search(index="articles", body=query_body)

    if results["hits"]["hits"]:
        return results["hits"]["hits"][0]
    return None

def GetArticle(title, source):
    query_body = {
        "query": {
            "bool": {
                "must": [
                {
                    "match": {
                        "Headline": title
                    }
                },
                {
                    "match": {
                        "Source": source
                    }
                }
                ]
            }
        }
    }

    results = es.search(index="articles", body=query_body)

    if results["hits"]["hits"]:
        return results["hits"]["hits"][0]
    return None

# Delete all indices (Reset DB)
def ResetDB():

    if not es:
        print("Couldn't connect to elasticsearch")
        return

    es.options(ignore_status=[400,404]).indices.delete(index='sources')
    es.options(ignore_status=[400,404]).indices.delete(index='articles')
    print("Database reset")

def UpdateLastScraped(id, time):
    es.update(index='sources',id=id,
        body={"doc": {"Last Retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ")}})


def EnableSource(id):
    es.update(index='sources',id=id,
        body={"doc": {"Active": True}})


def DisableSource(id):
    es.update(index='sources',id=id,
        body={"doc": {"Active": False}})