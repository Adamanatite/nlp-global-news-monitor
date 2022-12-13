import json
from transformers import AutoTokenizer, TFAutoModelForSeq2SeqLM




data = []

with open("classifier/datasets/en.json") as f:
    for line in f:
        d = json.loads(line)
        data.append((d["Text"], d["Category"]))

languages = ["fr", "es", "pt", "ru", "zh-C", "sw", "id", "ar", "ko"]

# batch_size = 100
# n = len(data) // batch_size

sentences = [d[0] for d in data]
categories = [d[1] for d in data]

with open("sentences.txt", "w") as f:
    for s in sentences:
        f.write(s + "\n") 
# print(sentences[:10])

# for lang in languages[:2]:
#     tokenizer = AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-en-{lang}")
#     model = TFAutoModelForSeq2SeqLM.from_pretrained(f"Helsinki-NLP/opus-mt-en-{lang}")

#     batch = tokenizer(sentences[:2], return_tensors="tf", padding=True, truncation=True)

#     generated_ids = model.generate(**batch)
#     translated_batch = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
#     print(translated_batch)