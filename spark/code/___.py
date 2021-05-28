from pyspark.sql import SparkSession 
from pyspark.sql.functions import aggregate, from_json, col, window, unix_timestamp, to_timestamp
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

# catania = signals \
#   .filter(signals.station_name == "Radio Maria") \
#   .select("time", "province", col("RSSI").cast("long")) \
#   .groupBy(window("time", "1 minutes", "1 minutes"), signals.province) \
#   .avg('RSSI')

# catania.writeStream \
#   .outputMode("complete") \
#   .format("console") \
#   .option("truncate", "false") \
#   .start() \
#   .awaitTermination()


catania = signals.filter(signals.province == "Catania") \
  .select("province", col("RSSI").cast('long')) \
  .groupBy("province").avg("RSSI")

messina = signals.filter(signals.province == "Messina") \
  .select("province", col("RSSI").cast('long')) \
  .groupBy("province").avg("RSSI")

joined = catania.union(messina)
joined.writeStream \
  .format("console") \
  .option("truncate", "false") \
  .start() \
  .awaitTermination()

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

# stampa tutto 

# signals.writeStream \
#   .format('console') \
#   .option("truncate", "false") \
#   .start() \
#   .awaitTermination()