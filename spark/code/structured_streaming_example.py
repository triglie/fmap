from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark import SparkContext
from pyspark.sql.functions import from_json, col, to_timestamp, unix_timestamp, window
from pyspark.sql.types import *
from sklearn.linear_model import LinearRegression
from elasticsearch import Elasticsearch


import pandas as pd


def get_spark_session():
    spark_conf = SparkConf()\
        .set('es.nodes', 'elasticsearch')\
        .set('es.port', '9200')
    sc = SparkContext(appName='rssi_signal_prediction', conf=spark_conf)
    return SparkSession(sc)


def get_rds_signal_schema():
    return StructType() \
        .add('station_name',  StringType(), True) \
        .add('RSSI',          StringType(), True) \
        .add('path',          StringType(), True) \
        .add('@timestamp',    StringType(), True) \
        .add('province',      StringType(), True) \
        .add('FM',            StringType(), True) \
        .add('@version',      StringType(), True) \
        .add('host',          StringType(), True) \
        .add('message',       StringType(), True) \
        .add('coords',        StringType(), True)


def get_rds_signal_stream(schema: StructType):
    return spark.readStream \
        .format('kafka') \
        .option('kafka.bootstrap.servers', 'kafkaserver:9092') \
        .option('subscribe', 'rds-signal-output') \
        .load() \
        .select('timestamp', 'value') \
        .withColumn('time', to_timestamp('timestamp', 'YYYY/MM/DD hh:mm:ss')) \
        .withColumn('json_content', col('value').cast('string')) \
        .withColumn('content', from_json(col('json_content'), schema)) \
        .select(col('time'), col('content.*')) \
        .withColumn('milliseconds', unix_timestamp('@timestamp', format="yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")) \
        .select(
            col('time'), 
            col('station_name'), 
            col('RSSI').cast('long'), 
            col('@timestamp'), 
            col('province'), 
            col('FM'), 
            col('coords'),
            col('milliseconds')
        )


def get_resulting_df_schema():
    return  StructType() \
        .add("@timestamp",      StringType()) \
        .add("station_name",    StringType()) \
        .add("province",        StringType()) \
        .add("estimated_RSSI",  LongType()) \
        .add("FM",              StringType()) \
        .add("coords",          StringType())


def get_output_df():
    return pd.DataFrame(columns=[
        '@timestamp', 
        'station_name', 
        'province', 
        'estimated_RSSI', 
        'FM', 
        'coords', 
    ])


def get_linear_regression_model(df: pd.DataFrame):
    x = df['milliseconds'].to_numpy().reshape(-1, 1)
    y = df['RSSI'].to_numpy()
    lr = LinearRegression()
    lr.fit(x, y)
    return lr 


def make_series(df, timestamp, predicted_rssi) -> pd.Series:
    return pd.Series([
        str(timestamp),
        df.iloc[0]['station_name'],
        df.iloc[0]['province'],
        int(predicted_rssi),
        df.iloc[0]['FM'],
        df.iloc[0]['coords']
    ], index=[
        '@timestamp', 
        'station_name', 
        'province', 
        'estimated_RSSI',
        'FM',
        'coords', 
    ])


def predict_value(model, milliseconds):
    rssi_range = lambda s: max(min(0, s), -70)
    s = model.predict([[milliseconds]])[0]
    return rssi_range(s)
    

def predict(df: pd.DataFrame) -> pd.DataFrame:    
    nrows = lambda df: df.shape[0]    
    newdf = get_output_df()
    if (nrows(df) < 1):
        return newdf
    model = get_linear_regression_model(df)
    lastSignalMillisec = df['milliseconds'].values.max()    
    next_minutes = [ (lastSignalMillisec + (60000 * i)) for i in range(5) ]
    next_rssi = [predict_value(model, m) for m in next_minutes]
    for millis, rssi in zip(next_minutes, next_rssi):
        newdf = newdf.append(make_series(df, millis, rssi), ignore_index=True)
    return newdf


if __name__ == "__main__":

    spark = get_spark_session()
    spark.sparkContext.setLogLevel("ERROR")
    schema = get_rds_signal_schema()
    signalStream = get_rds_signal_stream(schema)

    es_mapping = {
        "mappings": {
            "properties": {
                "@timestamp":       {"type": "date"},
                "estimated_RSSI":   {"type": "long"},
                "province":         {"type": "keyword"},
                "station_name":     {"type": "keyword"},
                "FM":               {"type": "keyword"},
                "coords":           {"type": "text"},
                "PI":               {"type": "keyword"}
            }
        }
    }

    es = Elasticsearch(host='elasticsearch')
    response = es.indices.create(
        index='rds-signal-output-spark', 
        body=es_mapping, 
        ignore=400
    )

    if 'acknowledged' in response:
        if response['acknowledged'] == True:
            print("Successfully created index:", response['index'])

    win = window(signalStream.time, "1 minutes")
    # signalStream \
    #     .groupBy('province', 'station_name', win) \
    #     .applyInPandas(predict, get_resulting_df_schema()) \
    #     .writeStream \
    #     .format('console') \
    #     .option("truncate", "false") \
    #     .start() \
    #     .awaitTermination()

    signalStream \
        .groupBy('province', 'station_name', win) \
        .applyInPandas(predict, get_resulting_df_schema()) \
        .writeStream \
        .option('checkpointLocation', '/save/location') \
        .format('es') \
        .start('rds-signal-output-spark') \
        .awaitTermination()