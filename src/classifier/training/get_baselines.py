from datasets import load_dataset, load_from_disk, ClassLabel
import evaluate
import numpy as np

BASE_DATASET = "valurank/News_Articles_Categorization"
LOCAL_DIR = "./.ml/"

# Process collected data
# Load dataset
try:
    collected_dataset = load_from_disk(LOCAL_DIR + "/datasets/collected_multilingual")
    print("Loaded local dataset")
except Exception as e:
    # Adapted from https://discuss.huggingface.co/t/how-to-create-custom-classlabels/13650
    def label_to_id(batch):
        batch["label"] = [label2id[cat] for cat in batch["label"]]
        return batch
    label2id = {"Entertainment/Arts": 0, "Sports": 1, "Politics": 2, "Science/Technology": 3, "Business/Finance": 4, "Health/Welfare": 5}
    collected_dataset = load_dataset('json', data_files=LOCAL_DIR + "datasets/multilingual/collected.json", split="train")
    features = collected_dataset.features.copy()
    text_category = ClassLabel(num_classes = 6, names=["Entertainment/Arts", "Sports", "Politics", "Science/Technology", "Business/Finance", "Health/Welfare"])
    features["label"] = text_category
    collected_dataset = collected_dataset.map(label_to_id, batched=True, features=features)
    collected_dataset = collected_dataset.shuffle(seed=42)
    
    collected_dataset.save_to_disk(LOCAL_DIR + "/datasets/collected_multilingual")
    print("Loaded dataset from original file")

print(collected_dataset)

# Split dataset based on fractions
test_split = 0.2

# Split train and test
dataset = collected_dataset.train_test_split(test_size=test_split)

# Load evaluation metric
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")


def stratified_sample(n):
    no_business = 2598
    no_sports = 2899
    no_scitech = 2239
    no_ent = 2555
    no_pol = 1328
    no_health = 1227

    dist = np.array([no_ent, no_sports, no_pol, no_scitech, no_business, no_health], dtype="float64")
    dist /= np.sum(dist)

    final_guesses = np.zeros(n)
    preds = np.random.uniform(0, 1, n)
    for i, p in enumerate(preds):
        x = 0
        for j, v in enumerate(dist):
            x += v
            if p < x:
                final_guesses[i] = j
                break
    return final_guesses

most_common = np.ones(len(dataset["test"]["label"]))
stratified_guesses = stratified_sample(len(dataset["test"]["label"]))

mc_acc = accuracy.compute(predictions=most_common, references=dataset["test"]["label"])["accuracy"]
mc_f1 = f1.compute(predictions=most_common, references=dataset["test"]["label"], average="weighted")["f1"]

strat_accs = np.zeros(3)
strat_f1s = np.zeros(3)

for i in range(3):
    sampling = stratified_sample(len(dataset["test"]["label"]))
    strat_accs[i] = accuracy.compute(predictions=sampling, references=dataset["test"]["label"])["accuracy"]
    strat_f1s[i] = f1.compute(predictions=sampling, references=dataset["test"]["label"], average="weighted")["f1"]

mc_acc *= 100
mc_f1 *= 100
strat_accs *= 100
strat_f1s *= 100



print("Most Common:")
print(f"Accuracy: {mc_acc:.4f}%")
print(f"F1: {mc_f1:.4f}")
print("Stratified Random Sampling:")
print(f"Accuracy: {np.mean(strat_accs):.4f}% +/- {np.std(strat_accs):.4f}")
print(f"F1: {np.mean(strat_f1s):.4f} +/- {np.std(strat_f1s):.4f}")

