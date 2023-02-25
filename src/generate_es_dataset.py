import elasticsearch as es
from database.elasticsearch_database import getInstance
import json

es = getInstance()

def get_query_body(lang):
    return {
        "query": {
            "term": {
                "Language": {
                    "value": lang
                }
            }
        }
    }

languages = ["en", "fr", "pt", "es", "zh", "id"]

total_len = 0

with open("./.ml/datasets/multilingual/collected.json", "w", encoding="utf-8") as f:
    for lang in languages:
        results = es.search(index="articles", body=get_query_body(lang), size=9999)["hits"]["hits"]
        total_len += len(results)
        for result in results:
            row = {}
            text_data = result["_source"]["Headline"] + " " + result["_source"]["Body"]
            cat_data = result["_source"]["Category"]
            row["text"] = text_data
            row["label"] = cat_data
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"Generated JSON file (n={total_len})")
