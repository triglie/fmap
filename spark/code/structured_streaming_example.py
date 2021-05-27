from __future__ import print_function

import sys

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

df.writeStream \
  .format("console") \
  .start() \
  .awaitTermination()