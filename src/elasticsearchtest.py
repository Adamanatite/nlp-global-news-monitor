from elasticsearch import Elasticsearch
import requests

response = requests.put("https://localhost:9200/_security/api_key", data={"name": "python_api_key"}, verify=False)
print(response)

# es = Elasticsearch(['https://adam:elastic@localhost:9200'])
# print(es.info().body)