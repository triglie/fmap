import requests 
import time

status=500
headers = {'Content-type': 'application/json'}
data = '{ "name": "elasticsearch-connector", "config": { "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector", "tasks.max": "1", "topics": "rds-signal-output", "key.ignore": "true", "schema.ignore": "true", "connection.url": "http://elasticsearch:9200", "type.name": "test-type", "name": "elasticsearch-sink" } }'

print("starting to requests")

while (status not in [200, 409]):
    time.sleep(2); 
    try:
        response = requests.post('http://connect:8083/connectors', headers=headers, data=data)
        status = response.status_code
    except Exception:
        status = 500
    
    if status not in [200, 409]:
        print(f"> current call got status code {status}, retrying in 2s.")
    else: 
        print(f"> current call got status code {status}, exiting.")