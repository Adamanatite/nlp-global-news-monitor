from transformers import pipeline, BertTokenizer, TFBertModel, TextClassificationPipeline
from datasets import load_dataset, load_from_disk
from googletrans import Translator

BASE_MODEL = "bert-base-multilingual-cased"
BASE_DATASET = "valurank/News_Articles_Categorization"
LOCAL_DIR = "./classifier/"

def gen_languages():

    t = Translator()

    # Load dataset
    try:
        dataset = load_from_disk(LOCAL_DIR + "/datasets/en")
        print("Loaded local dataset")
    except:
        dataset = load_dataset(BASE_DATASET)
        dataset.save_to_disk(LOCAL_DIR + "/datasets/en")
        print("Loaded dataset from huggingface")

    languages = ["fr", "es", "pt", "ru", "zh", "sw", "id", "ar", "ko"]
    for lang in languages:
        with open("classifier/datasets/" + lang + ".txt", "w") as f:
            for entry in dataset["train"]:
                trans = t.translate(entry["Text"], src="en", dest=lang)
                print(trans)
                f.write(trans + " -> " + entry["Category"] + "\n")

# gen_languages()
# exit()
# Load dataset
try:
    dataset = load_from_disk(LOCAL_DIR + "/datasets/en")
    print("Loaded local dataset")
except:
    dataset = load_dataset(BASE_DATASET)
    dataset.save_to_disk(LOCAL_DIR + "/datasets/en")
    print("Loaded dataset from huggingface")

print(dataset["train"][0]["Text"])
for split, data in dataset.items():
    data.to_json(LOCAL_DIR + f"/datasets/{split}.json")

# Load model
try:
    bert_tokenizer = BertTokenizer.from_pretrained(LOCAL_DIR + "model/")
    bert_model = TFBertModel.from_pretrained(LOCAL_DIR + "model/")
    print("Models loaded from local directory")
except:
    bert_tokenizer = BertTokenizer.from_pretrained(BASE_MODEL)
    bert_model = TFBertModel.from_pretrained(BASE_MODEL)

    bert_tokenizer.save_pretrained(LOCAL_DIR + "model/")
    bert_model.save_pretrained(LOCAL_DIR + "model/")
    print("Models loaded from huggingface")

text = "Replace me by any text you'd like."
encoded_input = bert_tokenizer(text, return_tensors='tf')
output = bert_model(encoded_input)

# bert_model = TextClassificationPipeline(tokenizer=bert_tokenizer, model=bert_model)
# bert_model.save_pretrained("./models/classifier/")
print(output)