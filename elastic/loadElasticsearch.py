import json

from elasticsearch import Elasticsearch

# very simple script to load scraped data into local Elasticsearch instance

LOCAL_URL = "http://localhost:9200"
INDEX_NAME = "uk_most_wanted"

connection = Elasticsearch(LOCAL_URL)

with open("UK_MWL_persons.json") as f:
    jsonData = json.load(f)

# loop through jsonData["persons"] array and load Elasticsearch index with data
for dataInd, data in enumerate(jsonData["persons"], 1):
    connection.index(index=INDEX_NAME, id=dataInd, body=data)
    print(f"Inserted document {dataInd} into Elasticsearch index")

connection.close()
