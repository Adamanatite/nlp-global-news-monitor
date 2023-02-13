import json
from googletrans import Translator
import time



data = []

with open(".ml/datasets/en.json") as f:
    for line in f:
        d = json.loads(line)
        data.append((d["Text"], d["Category"]))


languages = ["es"]
# languages = ["fr", "es", "pt", "ru", "zh-C", "sw", "id", "ar", "ko"]

# batch_size = 100
# n = len(data) // batch_size

sentences = [d[0] for d in data]
categories = [d[1] for d in data]

total = "||".join(sentences)
n = len(total)
i = 0
batches = []
while i < n - 5000:
    j = total[i:i+4999].rfind(".") + i + 1
    batches.append(total[i:j])
    i = j
batches.append(total[i:])

print("Sentences:", len(sentences))
# 3722
print("Batches:", len(batches))
# 3918

translator = Translator()
for lang in languages:
    with open(".ml/datasets/" + lang + ".txt", "w", encoding="utf-8") as f:
        last_error = False
        i = 0
        while i < len(batches):
            try:
                if i % 25 == 0:
                    print("i=", i)
                translation = translator.translate(batches[i], src="en", dest=lang).text
                f.write(translation + "//")
                i += 1
                if last_error:
                    print(i, "fixed")
                last_error = False
            except Exception as e:
                print(i, str(e))
                time.sleep(3)
                last_error = True
                continue
    
