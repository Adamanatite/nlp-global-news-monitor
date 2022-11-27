import newspaper
from langdetect import detect

    # Function for newspaper3k to create a parsed article
def article_parse(url, language=None):
    if language:
        article = newspaper.Article(url,language=language)
    else:
        article = newspaper.Article(url)
    article.download()
    article.parse()
    return article

article = article_parse("https://news.sina.com.cn/c/2022-11-23/doc-imqqsmrp7281728.shtml")
if article.text:
    print(article.text)
else:
    print("No body")

print("\n\n")

article2 = article_parse("https://news.sina.com.cn/c/2022-11-23/doc-imqqsmrp7281728.shtml", language="zh")
if article2.text:
    print(article2.text)
else:
    print("No body")

print("\n\n")
print(detect("Spanyol Vs Kosta Rika 3-0, 100 Gol La Roja di Piala Dunia"))
print("\n\n")

article3 = article_parse("https://bola.kompas.com/read/2022/11/23/23374488/spanyol-vs-kosta-rika-3-0-100-gol-la-roja-di-piala-dunia")
if article3.text:
    print(article3.text)
else:
    print("No body")

print("\n\n")

article4 = article_parse("https://bola.kompas.com/read/2022/11/23/23374488/spanyol-vs-kosta-rika-3-0-100-gol-la-roja-di-piala-dunia", language="id")
if article4.text:
    print(article4.text)
else:
    print("No body")