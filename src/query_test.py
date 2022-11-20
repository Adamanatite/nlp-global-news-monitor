from elasticsearch_database import GetSource, GetActiveSources

query_res = GetSource("https://www.bbc.co.uk/news")
print(query_res["_source"])

query_res2 = GetActiveSources()
print(len(query_res2))
print([query_res2[i]["_source"]["URL"] for i in range(len(query_res2))])