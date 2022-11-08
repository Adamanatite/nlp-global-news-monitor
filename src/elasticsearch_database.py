from elasticsearch import Elasticsearch
from datetime import datetime

try:
    es = Elasticsearch("http://localhost:9200")
except Exception as e:
    print(str(e))
    exit(-1)

print("Connected to elasticsearch server")


# Code is adapted from https://dylancastillo.co/elasticsearch-python/

# Create indexes
def CreateDB():
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

def AddSource(url, name, country, lang):
    doc = {
        "url": url,
        "name": name,
        "country": country,
        "language": lang,
        "active": True
    }

    try:
        es.index(index="sources", id=1, document=doc)
        print("Added source " + name)
        return True
    except Exception as e:
        print(str(e))
        return False

def AddArticle(url, title, text, date, source):
    doc = {
        "url": url,
        "title": title,
        "text": text,
        "publish_date": date,
        "scrape_date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "source": source
    }

    try:
        es.index(index="articles", id=1, document=doc)
        print("Added article " + title)
        return True
    except Exception as e:
        print(str(e))
        return False