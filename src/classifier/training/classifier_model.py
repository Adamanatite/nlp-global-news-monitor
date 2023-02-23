from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, DataCollatorWithPadding, create_optimizer
from transformers.keras_callbacks import KerasMetricCallback, PushToHubCallback
from datasets import load_dataset, load_from_disk, DatasetDict, ClassLabel
import evaluate
from evaluate import evaluator
import numpy as np
import tensorflow as tf

BASE_MODEL = "bert-base-multilingual-cased"
BASE_DATASET = "valurank/News_Articles_Categorization"
LOCAL_DIR = "./.ml/"

# Load dataset
try:
    dataset = load_from_disk(LOCAL_DIR + "/datasets/en")
    print("Loaded local dataset")
except Exception as e:
    # Adapted from https://discuss.huggingface.co/t/how-to-create-custom-classlabels/13650
    label2id = {"World": 0, "Politics" : 1, "Tech": 2, "Entertainment": 3, "Sports": 4, "Business": 5, "Health" : 6, "science": 7}
    def label_to_id(batch):
        batch["label"] = [label2id[cat] for cat in batch["label"]]
        return batch

    dataset = load_dataset(BASE_DATASET, split="train")
    dataset = dataset.rename_column("Text", "text")
    dataset = dataset.rename_column("Category", "label")

    features = dataset.features.copy()
    text_category = ClassLabel(num_classes = 8, names=["World", "Politics", "Technology", "Entertainment", "Sports", "Business", "Health", "Science"])
    features["label"] = text_category
    dataset = dataset.map(label_to_id, batched=True, features=features)

    dataset.save_to_disk(LOCAL_DIR + "/datasets/en")
    print("Loaded dataset from huggingface")


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
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_DIR + "model/", model_max_length=512)
    print("Tokenizer loaded from local directory")
except:
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, model_max_length=512)
    tokenizer.save_pretrained(LOCAL_DIR + "model/")
    print("Tokenizer loaded from huggingface")

#From https://huggingface.co/docs/transformers/main/en/training
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True)

tokenized_dataset = split_dataset.map(tokenize_function, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="tf")

label2id = {"World": 0, "Politics" : 1, "Technology": 2, "Entertainment": 3, "Sports": 4, "Business": 5, "Health" : 6, "Science": 7,}
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
precision = evaluate.load("precision")
recall = evaluate.load("recall")
f1 = evaluate.load("f1")
# From https://huggingface.co/spaces/BucketHeadP65/confusion_matrix
cfm = evaluate.load("BucketHeadP65/confusion_matrix")

# From https://huggingface.co/docs/transformers/main/en/tasks/sequence_classification
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)

    accuracy_score = accuracy.compute(predictions=predictions, references=labels)["accuracy"]
    precision_score = precision.compute(predictions=predictions, references=labels)["precision"]
    recall_score = recall.compute(predictions=predictions, references=labels)["recall"]
    f1_score = f1.compute(predictions=predictions, references=labels)["f1"]
    confusion_matrix = cfm.compute(predictions=predictions, references=labels)["confusion_matrix"]

    return {"precision": precision_score, "recall": recall_score, "f1": f1_score,
     "accuracy": accuracy_score, "confusion_matrix": confusion_matrix}

push_to_hub_callback = PushToHubCallback(
    output_dir="eng-news-topic-classifier",
    tokenizer=tokenizer,
)

# Train model
model.compile(optimizer=optimizer)
metric_callback = KerasMetricCallback(metric_fn=compute_metrics, eval_dataset=tf_validation_set)
model.fit(x=tf_train_set, validation_data=tf_validation_set, epochs=3, callbacks=[metric_callback, push_to_hub_callback])


task_evaluator = evaluator("text-classification")
# Evaluate model
eval_results = task_evaluator.compute(
    model_or_pipeline="lvwerra/distilbert-imdb",
    data=data, # Test splits
    metric=evaluate.combine(["accuracy", "recall", "precision", "f1"]),
    label_mapping={"NEGATIVE": 0, "POSITIVE": 1}
)
print(eval_results)

from evaluate.evaluation_suite import SubTask

class Suite(evaluate.EvaluationSuite):

    def __init__(self, name):
        super().__init__(name)
        self.preprocessor = lambda x: {"text": x["text"].lower()}
        self.suite = [
            SubTask(
                task_type="text-classification",
                data="glue",
                subset="sst2",
                split="validation[:10]",
                args_for_task={
                    "metric": "accuracy",
                    "input_column": "sentence",
                    "label_column": "label",
                    "label_mapping": {
                        "LABEL_0": 0.0,
                        "LABEL_1": 1.0
                    }
                }
            ),
            SubTask(
                task_type="text-classification",
                data="glue",
                subset="rte",
                split="validation[:10]",
                args_for_task={
                    "metric": "accuracy",
                    "input_column": "sentence1",
                    "second_input_column": "sentence2",
                    "label_column": "label",
                    "label_mapping": {
                        "LABEL_0": 0,
                        "LABEL_1": 1
                    }
                }
            )
        ]


# Save model
model.save_pretrained(LOCAL_DIR + "trained_model/")
