from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, window
from pyspark.sql.types import *
import random
import pandas as pd

spark = SparkSession \
    .builder \
    .appName('rssi_signal_prediction') \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType() \
    .add("station_name",  StringType(), True) \
    .add("RSSI",          StringType(), True) \
    .add("path",          StringType(), True) \
    .add("@timestamp",    StringType(), True) \
    .add("province",      StringType(), True) \
    .add("FM",            StringType(), True) \
    .add("@version",      StringType(), True) \
    .add("host",          StringType(), True) \
    .add("message",       StringType(), True) \
    .add("coords",        StringType(), True)

signals = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafkaserver:9092") \
    .option("subscribe", "rds-signal-output") \
    .load() \
    .select('timestamp', 'value') \
    .withColumn("time", to_timestamp("timestamp", "YYYY/MM/DD hh:mm:ss")) \
    .withColumn("json_value", col("value").cast("string")) \
    .withColumn("parsed_json", from_json(col("json_value"), schema)) \
    .select(
        col('time'),
        col('json_value'),
        col('parsed_json.*'),
    ) \
    .withColumn("_RSSI", col("RSSI").cast("long"))


def regression():
    return random.uniform(5, 200)


def g(df):
    grouped = df.groupby(["province", "station_name"])
    l = []
    for name, group in grouped:
        s = group['_RSSI'].values.sum()
        pro = name[0]
        sta = name[1]
        l.append({
            "station_name": sta,
            "province": pro,
            "_RSSI": s
        })
    return pd.DataFrame(l)


_schema = StructType() \
    .add("province", StringType()) \
    .add("station_name", StringType()) \
    .add("_RSSI", LongType())

df = signals \
    .groupBy("province", window(signals.time, "10 minutes")) \
    .applyInPandas(g, _schema) \

df \
    .writeStream \
    .format("console") \
    .outputMode("complete") \
    .start() \
    .awaitTermination()

# signals.writeStream \

#   .format("console") \
#   .start() \
#   .awaitTermination()
