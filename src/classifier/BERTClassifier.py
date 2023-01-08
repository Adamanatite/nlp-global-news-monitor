from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, DataCollatorWithPadding, create_optimizer, pipeline
from transformers.keras_callbacks import KerasMetricCallback, PushToHubCallback
from datasets import load_dataset, load_from_disk, DatasetDict, ClassLabel
import evaluate
import numpy as np
import tensorflow as tf

class BERTClassifier:

    def __init__(self, model_path, allow_model_training, data_src="valurank/News_Articles_Categorization", model_src="bert-base-multilingual-cased"):
        self.path = model_path
        self.allow_model_training = allow_model_training
        self.datasrc = data_src
        self.modelsrc = model_src
        self.tokenizer = self.load_tokenizer()
        # self.model = self.load_model()
        self.model = None
        print("Initialised Classifier")

    def load_dataset(self, test_split=0.2):
        # Load dataset
        try:
            dataset = load_from_disk(self.path + "/datasets/en")
            print("Loaded local dataset")
        except Exception as e:
            # Adapted from https://discuss.huggingface.co/t/how-to-create-custom-classlabels/13650
            label2id = {"World": 0, "Politics" : 1, "Tech": 2, "Entertainment": 3, "Sports": 4, "Business": 5, "Health" : 6, "science": 7}
            def label_to_id(batch):
                batch["label"] = [label2id[cat] for cat in batch["label"]]
                return batch

            dataset = load_dataset(self.dataset, split="train")
            dataset = dataset.rename_column("Text", "text")
            dataset = dataset.rename_column("Category", "label")

            features = dataset.features.copy()
            text_category = ClassLabel(num_classes = 8, names=["World", "Politics", "Technology", "Entertainment", "Sports", "Business", "Health", "Science"])
            features["label"] = text_category
            dataset = dataset.map(label_to_id, batched=True, features=features)

            dataset.save_to_disk(self.path + "/datasets/en")
            print("Loaded dataset from huggingface")

        # Split train
        train_test = dataset.train_test_split(test_size=test_split)
        # Split test and validation
        # Final data dict
        split_dataset = DatasetDict({
            'train': train_test['train'],
            'test': train_test['test']})
        return split_dataset

    def load_tokenizer(self):
        # Load tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.path + "trained_model/", model_max_length=512)
            print("Tokenizer loaded from local directory")
        except:
            tokenizer = AutoTokenizer.from_pretrained(self.modelsrc, model_max_length=512)
            tokenizer.save_pretrained(self.path + "trained_model/")
            print("Tokenizer loaded from huggingface")
        return tokenizer

    def load_model(self):
        label2id = {"World": 0, "Politics" : 1, "Technology": 2, "Entertainment": 3, "Sports": 4, "Business": 5, "Health" : 6, "Science": 7,}
        id2label = {v:k for k, v in label2id.items()}

        try:
            model = TFAutoModelForSequenceClassification.from_pretrained(
            self.path + "trained_model/", num_labels=8, id2label=id2label, label2id=label2id, local_files_only=True)
            print("Model loaded from local file")
        except Exception as e:
            print(str(e))
            if not self.allow_model_training:
                print("Couldn't load model")
                return None
            # Load model
            model = TFAutoModelForSequenceClassification.from_pretrained(
            self.modelsrc, num_labels=8, id2label=id2label, label2id=label2id)
            model = self.train_model(model)
            print("Model loaded from huggingface")
        return model
    
    def train_model(self, model):

        #From https://huggingface.co/docs/transformers/main/en/training
        def tokenize_function(examples):
            return self.tokenizer(examples["text"], truncation=True)

        split_dataset = self.load_dataset()
        tokenized_dataset = split_dataset.map(tokenize_function, batched=True)
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer, return_tensors="tf")

        batch_size = 16
        num_epochs = 5
        batches_per_epoch = len(tokenized_dataset["train"]) // batch_size
        total_train_steps = int(batches_per_epoch * num_epochs)
        optimizer, schedule = create_optimizer(init_lr=2e-5, num_warmup_steps=0, num_train_steps=total_train_steps)

        model.compile(optimizer=optimizer)

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
        metric_callback = KerasMetricCallback(metric_fn=compute_metrics, eval_dataset=tf_validation_set)
        # This is currently too memory intensive, so to integrate with scraping system for now training is skipped
        #model.fit(x=tf_train_set, validation_data=tf_validation_set, epochs=3, callbacks=[metric_callback])

        # Save model
        model.save_pretrained(self.path + "trained_model/")
        return model

    def classify(self, batch):
        if self.model is None:
            return ["Unknown" for i in range(len(batch))]
        # Do this outside classify method
        classifier = pipeline("text-classification", model=self.path + "trained_model/")
        inputs = [(a[1] + " " + a[2]) for a in batch]
        inputs = [i[:512] for i in inputs[:16]]
        results = classifier(inputs)
        categories = [r["label"] for r in results]
        print("Classified", len(batch), "articles.")
        return categories