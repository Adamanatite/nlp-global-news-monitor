import json
from googletrans import Translator




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
#     print(i)

# batches.append(total[i:])

# with open("batches.txt", "w") as f:
#     f.write("\n".join(batches))

# print(len(batches))

translator = Translator()
translation = translator.translate("Hello. How are you?||The sky is blue and I am feeling new.", src="en", dest="no").text
print(translation)
# for lang in languages:
#     for sentence in sentences:
#         translation = translator.translate(sentence, src="en", dest=lang).text