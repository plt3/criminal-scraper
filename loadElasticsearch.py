import json

from elasticsearch import Elasticsearch

# very simple script to load scraped data into local Elasticsearch instance

LOCAL_URL = "http://localhost:9200"
INDEX_NAME = "uk_most_wanted"

connection = Elasticsearch(LOCAL_URL)

with open("UK_MWL_persons.json") as f:
    jsonData = json.load(f)

for dataInd, data in enumerate(jsonData["persons"]):
    connection.index(index=INDEX_NAME, id=dataInd + 1, body=data)

connection.close()
