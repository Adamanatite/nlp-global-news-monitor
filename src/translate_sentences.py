import json
from googletrans import Translator

data = []

with open("classifier/datasets/en.json") as f:
    for line in f:
        d = json.loads(line)
        data.append((d["Text"], d["Category"]))

t = Translator()  

languages = ["fr", "es", "pt", "ru", "zh-CN", "sw", "id", "ar", "ko"]
all_data = {}

#batch_size = 100
#n = len(data) // batch_size

batch_size = 5
n = 2

sentences = [d[0] for d in data]
categories = [d[1] for d in data]

for lang in languages:
    lang_data = []
    for i in range(3):
        print(lang)
        trans = t.translate(sentences[i], src="en", dest=lang)
        lang_data.append((trans.text, categories[i]))
    all_data[lang] = lang_data
print(all_data)