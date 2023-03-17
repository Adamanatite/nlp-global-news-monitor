import elasticsearch as es
from database.database_connector import getInstance
import json
import random

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
skipped_sci = 0
skipped_bus = 0

with open("./.ml/datasets/multilingual/collected.json", "w", encoding="utf-8") as f:
    for lang in languages:
        results = es.search(index="articles", body=get_query_body(lang), size=9999)["hits"]["hits"]
        total_len += len(results)
        for result in results:
            row = {}
            text_data = result["_source"]["Headline"] + " " + result["_source"]["Body"]
            cat_data = result["_source"]["Category"]
            # Downsampling
            if lang == "zh" and cat_data == "Business/Finance":
                if random.randint(0, 3) != 2:
                    skipped_bus += 1
                    continue
            elif lang == "zh" and cat_data == "Science/Technology":
                if random.randint(0,1) != 0:
                    skipped_sci += 1
                    continue
            row["text"] = text_data
            row["label"] = cat_data
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"Generated JSON file (n={total_len - skipped_sci - skipped_bus})")
print(f"Skipped {skipped_bus} business articles")
print(f"Skipped {skipped_sci} science articles")
