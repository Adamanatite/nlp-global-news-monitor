from classifier.BERTClassifier import BERTClassifier

classifier = BERTClassifier("./.ml/", False)
texts = ["Hello this is some sort of news article",
"This is also a news article I guess maybe sports"]

classified = classifier.classify(texts)
print(classified)