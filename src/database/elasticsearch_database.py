from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import json
import os
# Get current directory from project tree
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
this_dir = str(parentdir) + "/database/"


def ESCloudConnect():
    # Get data from JSON file
    with open(this_dir + "data/db_info.json") as f:
        data = json.load(f)

    ELASTIC_USERNAME = data["username"]
    ELASTIC_PASSWORD = data["cloud_password"]
    CERT_PATH = data["cert_path"]

    # Connect to database (adapted from https://www.elastic.co/guide/en/elasticsearch/client/python-api/master/connecting.html)
    try:
        es = Elasticsearch(
        cloud_id='Biocaster_test_kibana:ZXVyb3BlLXdlc3QyLmdjcC5lbGFzdGljLWNsb3VkLmNvbTo0NDMkNzU0ZWQ4N2IzNzkxNGY4OGEyMDIxMjliMzU2YmJjZWUkYTU4M2E3ZWM2YjQ5NDM1YThiMGQ4MjFkOGIwN2I3Yzg=',
        http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))
        print("Connected")
    except Exception as e:
        print(str(e))
        return None

    # From https://stackoverflow.com/a/31644507
    if not es.ping():
        print("Couldn't connect")
        return None

    return es   

# Return es connection, or None if it failed
def ESConnect():

    # Get data from JSON file
    with open(this_dir + "data/db_info.json") as f:
        data = json.load(f)

    USE_CLOUD = data["connection_type"].lower() == "cloud"
    ELASTIC_USERNAME = data["username"]
    ELASTIC_PASSWORD = data["password"]
    CLOUD_USERNAME = data["cloud_username"]
    CLOUD_PASSWORD = data["cloud_password"]
    CERT_PATH = data["cert_path"]

    # Connect to database (adapted from https://www.elastic.co/guide/en/elasticsearch/client/python-api/master/connecting.html)
    try:
        if USE_CLOUD:
            es = Elasticsearch(
            cloud_id='Biocaster_test_kibana:ZXVyb3BlLXdlc3QyLmdjcC5lbGFzdGljLWNsb3VkLmNvbTo0NDMkNzU0ZWQ4N2IzNzkxNGY4OGEyMDIxMjliMzU2YmJjZWUkYTU4M2E3ZWM2YjQ5NDM1YThiMGQ4MjFkOGIwN2I3Yzg=',
            http_auth=(CLOUD_USERNAME, CLOUD_PASSWORD))
        else:
            es = Elasticsearch(
            "https://localhost:9200",
            ca_certs=this_dir + CERT_PATH,
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


def AddArticle(url, title, text, country, lang, date, source, scraper, category=None, skip_verification=False):
    
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
        "Category": category
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

def AddArticles(articles, categories):
    
    if not es:
        return

    actions = [
        {
        "_index": "articles",
        "_source": {
            "URL": article[0],
            "Headline": article[1],
            "Body": article[2],
            "Country": article[3],
            "Language": article[4],       
            "Published": article[5],
            "Retrieved": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Source": article[6],
            "Data Source": article[7],
            "Category": category
            }
        } 
    for article, category in zip(articles, categories)]

    try:
        helpers.bulk(es, actions)
        print("Added", len(articles), "articles")
    except Exception:
        print("Couldn't add articles, adding individually")
        for article, category in zip(articles, categories):
            try:
                AddArticle(article[0], article[1], article[2], article[3], article[4], article[5], article[6], article[7], category)
            except Exception as e:
                print(str(e))
                continue

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

def GetActiveSources(value=True, max_scrapers=1000):

    if not es:
        return []

    query_body = {
        "size": max_scrapers,
        "query": {
            "match": {
                "Active": value
            }
        }
    }

    results = es.search(index="sources", body=query_body)

    if results["hits"]["hits"]:
        return results["hits"]["hits"]
    return []

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