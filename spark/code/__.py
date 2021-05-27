from __future__ import print_function

import json

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.dataframe import DataFrame

def elaborate(batch_df: DataFrame, batch_id: int):
  batch_df.show(truncate=False)

sc = SparkContext(appName="example")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafkaserver:9092") \
  .option("subscribe", "rds-signal-output") \
  .load()

# casted_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
# signal_df = casted_df.select('value').rdd.map(lambda x: json.loads(x)).toDF()

# query = signal_df.writeStream.format('console').start()

query = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
  .select('value').rdd.map(lambda x: json.loads(x)).toDF() \
  .writeStream.format('console').start().awaitTermination()

# query = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
#   .writeStream \
#   .format("console") \
#   .start()

# df.writeStream \
#   .format("console") \
#   .start() \
#   .awaitTermination()