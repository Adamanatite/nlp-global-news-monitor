import random
from classifier.classifier import Classifier


class RandomClassifier(Classifier):
    """
    Concrete classifier implementation for a classifier which randomly selects category
    """
    def __init__(self, categories):
        """
        Initialise model parameters

        :param categories: The list of categories to randomly choose from
        """
        # Initialise list of categories
        self.categories = categories

        # Call abstract constructor
        super().__init__("", "")
        print("Initialised Dummy Classifier")


    def classify_batch(self, batch):
        """
        Classifies a batch of inputs randomly and returns the classes

        :param batch: The batch of inputs to be classified
        :returns: The list of corresponding input item classes
        """
        return [random.choice(self.categories) for item in batch]