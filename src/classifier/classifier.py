from database.database_connector import add_articles

class Classifier:
    """
    Abstract classifier class which contains the consistent logic of a classifier module.
    To be inherited by specific classifier subclasses
    """
    def __init__(self, tokenizer_path, model_path, batch_size=16):
        """
        Initialises the variables and loads the tokenizer and model
        :param tokenizer_path: The path to the tokenizer
        :param model_path: The path to the model
        :param batch_size: The size pf batches to be classified (default is 16)
        """
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.batch_size = batch_size

        self.tokenizer = self.load_tokenizer()
        self.model = self.load_model()


    def load_tokenizer(self):
        """
        Abstract method for loading the tokenizer to be overridden
        in a concrete classifier implementation

        :returns: The loaded tokenizer object
        """
        return []


    def load_model(self):
        """
        Abstract method for loading the model to be overridden
        in a concrete classifier implementation

        :returns: The loaded model object
        """
        return []


    def prepare_inputs(self, items):
        """
        Prepares the given inputs for tokenization.
        To be overridden by a concrete implementation

        :param items: The input data items  
        :returns: The prepared data items
        """
        return items


    def tokenize_inputs(self, inputs):
        """
        Tokenizes the given input items
        To be overridden by a concrete implementation

        :param items: The input prepared data items  
        :returns: The tokenized data items
        """
        return inputs


    def classify(self, items):
        """
        Given a list of items, assigns a class to each of them and commits the
        articles to the database

        :param items: The data items to classify
        :raises IndexError: If each article does not have a given category
        """
        # Process input items
        prepared_items = self.prepare_inputs(items)
        tokenized_items = self.tokenize_inputs(prepared_items)

        # Classify in batches
        classes = []
        while len(tokenized_items) > self.batch_size:
            batch = tokenized_items[:self.batch_size]
            batch_classes = self.classify_batch(batch)
            classes += batch_classes
            tokenized_items = tokenized_items[self.batch_size:]
        classes += self.classify_batch(tokenized_items)
        print(classes)

       # Ensure we have the correct number of categories
        if len(classes) != len(items):
            raise IndexError("Mismatch in classifier: Not the same number of items and classes")

        # Commit articles to database
        add_articles(items, classes)


    def classify_batch(self, batch):
        """
        Abstract method for classifying a batch of input items
        To be overridden in a concrete classifier implementation

        :returns: The list of classes corresponding to a class for each item in the batch
        """
        return ["Unknown" for item in batch]
