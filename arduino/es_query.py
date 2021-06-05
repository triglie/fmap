import requests

data = """{
  "query": { "match": {"PI": "505a"} }
}"""

url="http://localhost:9200/rds-signal-output/_search?pretty"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

r = requests.post(url,data=data, headers=headers)

print(r.json())

