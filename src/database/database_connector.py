from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import json
import os

# Get current directory from project tree
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
this_dir = str(parentdir) + "/database/"


def es_connect():
    """
    Creates a database connection instance
    :returns: an instance of the database connection
    """
    # Get data from JSON file
    with open(this_dir + "data/db_info.json") as f:
        data = json.load(f)

    USE_CLOUD = data["connection_type"].lower() == "cloud"
    ELASTIC_USERNAME = data["local_username"]
    ELASTIC_PASSWORD = data["local_password"]
    CLOUD_ID = data["cloud_id"]
    CLOUD_USERNAME = data["cloud_username"]
    CLOUD_PASSWORD = data["cloud_password"]
    CERT_PATH = data["cert_path"]

    # Connect to database (adapted from https://www.elastic.co/guide/en/elasticsearch/client/python-api/master/connecting.html)
    try:
        if USE_CLOUD:
            conn = Elasticsearch(
            cloud_id=CLOUD_ID,
            http_auth=(CLOUD_USERNAME, CLOUD_PASSWORD))
        else:
            conn = Elasticsearch(
            "https://localhost:9200",
            ca_certs=this_dir + CERT_PATH,
            basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
            )
    except Exception as ex:
        print(str(ex))
        return None

    # From https://stackoverflow.com/a/31644507
    if not conn.ping():
        return None

    return conn


def get_instance():
    """
    Returns a database connection instance

    :returns: an instance of the database connection
    """
    return es


def reset_db():
    """
    Resets the database, deleting all indices
    """
    if not es:
        print("Couldn't connect to elasticsearch")
        return

    es.options(ignore_status=[400,404]).indices.delete(index='sources')
    es.options(ignore_status=[400,404]).indices.delete(index='articles')
    print("Database reset")


# Create indices
def create_db():
    """
    Creates the database indices if they don't exist
    """
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
                "Source Type": {"type": "keyword"},
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
                "Source Type": {"type": "keyword"},
                "Category": {"type": "keyword"}
        }
    }

    if not es.indices.exists(index="articles"):
        es.indices.create(index="articles", mappings=article_mappings)
        print("Created articles index")


def add_article(url, title, text, country, lang, date, source, source_type, category=None):
    """
    Adds an article to the datbase given its details

    :param url: The article URL
    :param title: The article title
    :param text: The article main body text
    :param country: The country the article originates from
    :param lang: The language the article is written in
    :param date: The date the article was published
    :param source: The source which found the article
    :param source_type: The type of source which found the article
    :param category: The article category (default is None)  
    :returns: The ID of the added article
    """
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
        "Source Type": source_type,
        "Category": category
    }

    try:
        if not get_article_from_title(title,source):
            res = es.index(index="articles", document=doc)
            print(source + " added article " + title)
            return res["_id"]
        return None
    except Exception as ex:
        print(source + " couldn't add article " + title)
        print(str(ex))
        return None


def add_articles(articles, categories):
    """
    Adds a batch of articles to the database at once. 
    If it fails, it will add them individually.

    :param articles: The list of articles to add
    :param categories: The list of corresponding categories
    """
    if not es:
        return

    actions = [
        {
        "_index": "articles",
        "_source": {
            "URL": article["url"],
            "Headline": article["title"],
            "Body": article["text"],
            "Country": article["lang"],
            "Language": article["country"],       
            "Published": article["date"],
            "Retrieved": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Source": article["source"],
            "Source Type": article["source_type"],
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
                add_article(article["url"], article["title"], article["text"], article["lang"], article["country"], article["date"], article["source"], article["source_type"], category)
            except Exception as ex:
                print(str(ex))
                continue

# Article duplicate checking

def get_article_from_url(url):
    """
    Attempts to retrieve an article from the database with a given URL

    :param url: The URL to search for
    :returns: The found article, or None if no article is found
    """
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


def get_article_from_title(title, source):
    """
    Attempts to retrieve an article from the database with a given title and source name

    :param title: The title to search for
    :param source: The source to search for
    :returns: The found article, or None if no article is found
    """
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

# Loading sources

def get_source(url):
    """
    Attempts to retrieve a source from a given URL

    :param title: The title to search for
    :param url: The URL to search for
    :returns: The found source, or None if no source is found
    """
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


def get_sources(max_sources=1000):
    """
    Gets up to the maximum specified number of sources and returns their details

    :param max_sources: The maximum number of sources to return (default 1000)
    :returns: The list of sources found
    """
    if not es:
        return []

    query_body = {
        "size": max_sources
    }

    results = es.search(index="sources", body=query_body)

    if results["hits"]["hits"]:
        return results["hits"]["hits"]
    return []


# Source updating

# Add a source to the database
def add_source(url, name, country, lang, source_type):
    """
    Adds a source to the database given its details

    :param url: The source URL
    :param name: The source name
    :param country: The origin country of the source
    :param lang: The primary language of the source
    :param source_type: The type of source
    :returns: The ID of the newly added source
    """
    if not es:
        return

    doc = {
        "URL": url,
        "Name": name,
        "Country": country,
        "Language": lang,
        "Source Type": source_type,
        "Last Retrieved": None,
        "Active": True
    }

    try:
        if not get_source(url):
            res = es.index(index="sources", document=doc)
            print("Added source " + name)
            return res["_id"]
        return None
    except Exception as ex:
        print("Couldn't add source " + name)
        print(ex)
        return None


def update_last_scraped(source_id, time):
    """
    Updates the last scraped time of a source with 
    the specified ID to the specified time in the database

    :param source_id: The source ID
    :param time: The time to update to
    """
    es.update(index='sources', id=source_id,
        body={"doc": {"Last Retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ")}})


def enable_source(source_id):
    """
    Sets the source with given source ID to enabled on the database

    :param source_id: The source ID to enable
    """   
    es.update(index='sources', id=source_id,
        body={"doc": {"Active": True}})


def disable_source(source_id):
    """
    Sets the source with given source ID to disabled on the database

    :param source_id: The source ID to disable
    """ 
    es.update(index='sources', id=source_id,
        body={"doc": {"Active": False}})

def delete_source(source_id):
    """
    Attempts to deletethe source with given source ID from the database

    :param source_id: The source ID to delete
    :returns: A boolean indicating whether the deletion was successful
    """ 
    try:
        es.delete(index="sources", id=source_id)
        return True
    except Exception as ex:
        print(str(ex))
        return False

# Get DB connection instance
es = es_connect()