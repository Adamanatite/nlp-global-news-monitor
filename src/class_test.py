from classifier.BERTClassifier import BERTClassifier

classifier = BERTClassifier("./.ml/", False)
texts = [(None, "Hello this is some sort of news article", "And this"),
(None, "This is also a news article I guess maybe sports", "Cristiano Ronaldo")]

classified = classifier.classify(texts)
print(classified)