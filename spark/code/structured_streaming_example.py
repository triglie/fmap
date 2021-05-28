from pyspark.sql import SparkSession 
from pyspark.sql.functions import from_json, col, window, unix_timestamp, to_timestamp
from pyspark.sql.types import *

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
    col('parsed_json.*')
  )

#
# Uncomment to enable group by 
#

# signalsStacked = (
#   signals.withWatermark("time", "1 minutes") \
#     .groupBy(col("province"), "time") \
#     .count()
# )

# signalsStacked \
#   .writeStream \
#   .format('console') \
#   .start() \
#   .awaitTermination()

signals.writeStream \
  .format('console') \
  .option("truncate", "false") \
  .start() \
  .awaitTermination()