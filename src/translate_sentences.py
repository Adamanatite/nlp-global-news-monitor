import json
from googletrans import Translator
import time



data = []

with open(".ml/datasets/en.json") as f:
    for line in f:
        d = json.loads(line)
        data.append((d["Text"], d["Category"]))


languages = ["fr", "es", "pt", "ru", "zh-C", "sw", "id", "ar", "ko"]

# batch_size = 100
# n = len(data) // batch_size

sentences = [d[0] for d in data]
categories = [d[1] for d in data]

# total = "||".join(sentences)
# n = len(total)
# i = 0
# batches = []
# while i < n - 5000:
#     j = total[i:i+4999].rfind(".") + i + 1
#     batches.append(total[i:j])
#     i = j
# batches.append(total[i:])

# print("Sentences:", len(sentences))
# # 3722 articles
# print("Batches:", len(batches))
# # 3918 batches

translator = Translator()

for lang in languages:
    with open(".ml/datasets/" + lang + ".txt", "w", encoding="utf-8") as f:
        print(lang)
        print("-----------------")
        c = 0
        for sentence in sentences:
            # Put sentences into batches of 5000 characters
            n = len(sentence)
            k = 0
            batches = []
            while k < n - 5000:
                j = sentence[k:k+4999].rfind(".") + k + 1
                batches.append(sentence[k:j])
                k = j
            batches.append(sentence[k:])
            
            i = 0
            while i < len(batches):
                try:
                    if c % 25 == 0:
                        print("c=", c)
                    translation = translator.translate(batches[i], src="en", dest=lang).text
                    f.write(translation + " ")
                    i += 1
                    c += 1
                except Exception as e:
                    print(c, i, str(e))
                    time.sleep(3)
                    continue
            f.write("\n")
    
