#!/bin/bash

while :
do
  if ping -c 1 connect &> /dev/null
  then
    curl -XPOST -H "Content-type: application/json" -d '{
    "name": "elasticsearch-connector",
    "config": {
        "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
        "tasks.max": "1",
        "topics": "rds-signal-output",
        "key.ignore": "true",
        "schema.ignore": "true",
        "connection.url": "http://elasticsearch:9200",
        "type.name": "test-type",
        "name": "elasticsearch-sink"
        }
    }' 'http://connect:8083/connectors'
    break
  fi
  sleep 5
done