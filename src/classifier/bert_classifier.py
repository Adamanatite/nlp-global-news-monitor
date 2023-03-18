import torch
from transformers import XLMRobertaTokenizerFast, XLMRobertaForSequenceClassification
from classifier.classifier import Classifier


class BERTClassifier(Classifier):
    """
    Concrete classifier implementation for an XLM-RoBERTA based classifier 
    using huggingface
    """
    def __init__(self, local_path, tokenizer_path, batch_size=32):
        """
        Initialise model parameters

        :param local_path: The local directory where model and tokenizer will
        be stored or saved
        :param tokenizer_path: The path to the tokenizer
        :param batch_size: The size pf batches to be classified (default is 32)
        """
        # Add trailing backslash
        if not local_path[-1] == "/":
            local_path += "/"

        self.local_path = local_path

        # Call abstract constructor (model uses local path)
        super().__init__(tokenizer_path, local_path + "model/", batch_size)
        print("Initialised BERT Classifier")

    def load_tokenizer(self):
        """
        Loads the tokenizer from a local file or from online, and saves to local file

        :returns: The tokenizer object
        """
        # Load tokenizer
        try:
            tokenizer = XLMRobertaTokenizerFast.from_pretrained(self.local_path + "tokenizer/")
            print("Tokenizer loaded from local directory")
        except Exception:
            tokenizer = XLMRobertaTokenizerFast.from_pretrained(self.tokenizer_path)
            tokenizer.save_pretrained(self.local_path + "tokenizer/")
            print("Tokenizer loaded from huggingface")
        return tokenizer


    def load_model(self):
        """
        Loads the pretrained model from a local file

        :returns: The model object
        """
        label2id = {"Entertainment/Arts": 0, "Sports": 1, "Politics": 2, "Science/Technology": 3, "Business/Finance": 4, "Health/Welfare": 5}
        id2label = {v:k for k, v in label2id.items()}
        # Load model
        model = XLMRobertaForSequenceClassification.from_pretrained(
            self.model_path, num_labels=6, id2label=id2label, label2id=label2id)
        print("Model loaded")
        return model


    def prepare_inputs(self, items):
        """
        Prepares inputs for tokenization by concatenating headline and body

        :param items: The batch of input items to be classified
        :returns: The prepared input list
        """
        return [i["title"] + " " + i["text"] for i in items]


    def tokenize_inputs(self, items):
        """
        Uses the tokenizer to tokenize the prepared inputs for classification

        :param items: The batch of prepared input items to be tokenized
        :returns: The tokenized inputs
        """
        return self.tokenizer(items, truncation=True, padding=True, return_tensors="pt")["input_ids"]


    def classify_batch(self, batch):
        """
        Classifies a batch of inputs and returns the classes

        :param batch: The batch of inputs to be classified
        :returns: The list of corresponding input item classes
        """
        with torch.no_grad():
            logits = self.model(batch).logits
            predicted_class_ids = logits.argmax(axis=1).numpy()
            predictions = [self.model.config.id2label[i] for i in predicted_class_ids]
        print(predictions)
        return predictions