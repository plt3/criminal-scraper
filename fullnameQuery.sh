# Short script to query local Elasticsearch instance with scraped data stored in index
# called "uk_most_wanted" for an individual criminal's full name

# See MooganQuery.json and MooganQuery.png for output of this script

# Elasticsearch index search endpoint
elasticUrl="localhost:9200/uk_most_wanted/_search?pretty"

# full name of criminal to search for
fullName="Michael Paul Moogan"

# split full name into first name(s) and last name to support both 2 and 3+ word names
firstName=$(echo $fullName | sed 's|\(.*\) .*|\1|')
lastName=$(echo $fullName | sed 's|.* ||')

# make request to Elasticsearch endpoint asking to match either first or last name,
# can also change bool.should to bool.must for stricter matching
curl -X GET "$elasticUrl" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "firstname": "'"$firstName"'"
          }
        },
        {
          "match": {
            "lastname": "'"$lastName"'"
          }
        }
      ]
    }
  }
}
'
