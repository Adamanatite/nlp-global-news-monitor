from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, DataCollatorWithPadding, create_optimizer
from transformers.keras_callbacks import KerasMetricCallback, PushToHubCallback
from datasets import load_dataset, load_from_disk, DatasetDict
import evaluate
import numpy as np
import tensorflow as tf

BASE_MODEL = "bert-base-multilingual-cased"
BASE_DATASET = "valurank/News_Articles_Categorization"
LOCAL_DIR = "./classifier/"

# Load dataset
try:
    dataset = load_from_disk(LOCAL_DIR + "/datasets/en")
    print("Loaded local dataset")
except Exception as e:
    print(str(e))
    dataset = load_dataset(BASE_DATASET, split="train")
    dataset.save_to_disk(LOCAL_DIR + "/datasets/en")
    print("Loaded dataset from huggingface")

print(dataset.features)

text_category = ClassLabel(num_classes = 8,names=["negative", "neutral", "positive"])

# Split dataset based on fractions
train_split, test_split = 0.8, 0.2

# Split train
train_test = dataset.train_test_split(test_size=test_split)
# Split test and validation
# Final data dict
split_dataset = DatasetDict({
    'train': train_test['train'],
    'test': train_test['test']})

# Load tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_DIR + "model/")
    print("Tokenizer loaded from local directory")
except:
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.save_pretrained(LOCAL_DIR + "model/")
    print("Tokenizer loaded from huggingface")

#From https://huggingface.co/docs/transformers/main/en/training
def tokenize_function(examples):
    return tokenizer(examples["Text"], truncation=True)

tokenized_dataset = split_dataset.map(tokenize_function, batched=True)
print(tokenized_dataset["train"][0]["Category"])

data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="tf")

label2id = {"World": 0, "Politics" : 1, "Tech": 2, "Entertainment": 3, "Sports": 4, "Business": 5, "Health" : 6, "science": 7,}
id2label = {v:k for k, v in label2id.items()}


batch_size = 16
num_epochs = 5
batches_per_epoch = len(tokenized_dataset["train"]) // batch_size
total_train_steps = int(batches_per_epoch * num_epochs)
optimizer, schedule = create_optimizer(init_lr=2e-5, num_warmup_steps=0, num_train_steps=total_train_steps)

# Load model
model = TFAutoModelForSequenceClassification.from_pretrained(
BASE_MODEL, num_labels=8, id2label=id2label, label2id=label2id)
print("Model loaded from huggingface")

# Initialise datasets
tf_train_set = model.prepare_tf_dataset(
    tokenized_dataset["train"],
    shuffle=True,
    batch_size=16,
    collate_fn=data_collator,
)

tf_validation_set = model.prepare_tf_dataset(
    tokenized_dataset["test"],
    shuffle=False,
    batch_size=16,
    collate_fn=data_collator,
)

# Load evaluation metric
accuracy = evaluate.load("accuracy")

# From https://huggingface.co/docs/transformers/main/en/tasks/sequence_classification
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)

# Train model
model.compile(optimizer=optimizer)
metric_callback = KerasMetricCallback(metric_fn=compute_metrics, eval_dataset=tf_validation_set, label_cols=["Category"])
model.fit(x=tf_train_set, validation_data=tf_validation_set, epochs=3, callbacks=[metric_callback])

# Save model
model.save_pretrained(LOCAL_DIR + "trained_model/")
