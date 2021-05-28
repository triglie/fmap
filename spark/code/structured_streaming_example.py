from pyspark.sql import SparkSession 
from pyspark.sql.functions import from_json, col, create_map
from pyspark.sql.types import *

spark = SparkSession \
  .builder \
    .appName('rssi_signal_prediction') \
      .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType() \
  .add("RSSI", LongType()) \
  .add("province", StringType()) \
  .add("station_name", StringType()) \
  .add("FM", StringType()) \
  .add("location", StringType()) \
  .add("PI", StringType(), True)

signals = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafkaserver:9092") \
  .option("subscribe", "rds-signal-output") \
  .load() \
  .select('timestamp', 'value') \
  .withColumn("parsed_json", from_json(col("value").cast("string"), schema))\
  .select(col('timestamp'), col('value'), col('parsed_json.*'))\

# signals_ = signals \
#   .select(from_json(col("value").cast("string"), schema) \
#   .alias("parsed_value")) \
#   .writeStream \
#   .format('console') \
#   .start() \
#   .awaitTermination()

signals.writeStream \
  .format('console') \
  .start() \
  .awaitTermination()

# query = signals \
#   .groupBy('parsed_value.province', window('parsed_value', '1 hour')) \
#   .count() \
#   .writeStream \
#   .format("console") \
#   .start()

# query.awaitTermination()