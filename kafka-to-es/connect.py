from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import json
import requests
import time 

def wait_until_es_is_up():
    status = None 
    while (True):
        time.sleep(1)
        try:
            response = requests.get('http://elasticsearch:9200/')
            status = response.status_code
            print(f'got status {status}')
        except Exception: 
            print('retrying.')
        if (status is not None and status in [200]):
            print('connected to elasticsearch.')
            return 


def wait_until_kafka_is_up():
    """Kafka may be up (kafka doesn't provides http endpoints)."""
    time.sleep(25)


def format_coords_as_geopoint(coords):
    lat, lon = coords.split(',')
    return {
        "lat": float(lat), 
        "lon": float(lon)
    }


def correct_message_format(msg: dict):
    return {
        '@timestamp':   msg.get('@timestamp'), 
        'RSSI':         int(msg.get('RSSI')), 
        'province':     msg.get('province'), 
        'station_name': msg.get('station_name'), 
        'FM':           msg.get('FM'), 
        'location':     format_coords_as_geopoint(msg.get('coords')), 
        'PI':           msg.get('PI', None)
    }


def create_es_index_mapping(es):
    es.indices.create(index='rds-signal-output', body={
        "mappings": {
            "properties": {
                "@timestamp":   {"type": "date", "format": "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"},
                "RSSI":         {"type": "long"},
                "province":     {"type": "keyword"},
                "station_name": {"type": "keyword"},
                "FM":           {"type": "keyword"},
                "location":     {"type": "geo_point"},
                "PI":           {"type": "keyword"}
            }
        }
    }, ignore=400)


def ingest_msg_to_elasticsearch(msg, es):
    es.index(
        index='rds-signal-output', 
        body=msg, 
    )


if __name__ == "__main__":
    wait_until_es_is_up()
    wait_until_kafka_is_up()

    json_deserializer = lambda msg: json.loads(msg.decode('utf-8'))

    try:

        kconsumer = KafkaConsumer('rds-signal-output',
            client_id='kafka-to-es-consumer', 
            group_id ='kafka-to-es', 
            bootstrap_servers=['kafkaserver:9092'],
            value_deserializer=json_deserializer)

        elasticsearch = Elasticsearch([{'host':'elasticsearch', 'port': 9200}])
        create_es_index_mapping(elasticsearch)

        for message in kconsumer:
            print('sending message to es.')
            message = correct_message_format(message.value)
            ingest_msg_to_elasticsearch(message, elasticsearch)

    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)


