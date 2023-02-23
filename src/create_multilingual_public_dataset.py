import json

categories = []

with open("./.ml/datasets/multilingual/test.json", "w", encoding="utf-8") as f:
    with open(".ml/datasets/en.json") as inf:
        for line in inf:
            d = json.loads(line)
            data = {}
            data["text"] = d["Text"]
            data["label"] = d["Category"]
            f.write(json.dumps(data) + "\n")
            categories.append(d["Category"])

    languages = ["fr", "es", "pt", "zh-CN", "id"]
    for lang in languages:
        with open(".ml/datasets/" + lang + ".txt", encoding="utf-8") as inf:
            for i, line in enumerate(inf):
                data = {}
                data["text"] = line
                data["label"] = categories[i]
                f.write(json.dumps(data) + "\n")