from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, window
from pyspark.sql.types import *
import random
import pandas as pd


def get_spark_session():
    return SparkSession \
        .builder \
        .appName('rssi_signal_prediction') \
        .getOrCreate()


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
        .withColumn('_RSSI', col('RSSI').cast('long'))


# def regression(dataframe: pd.DataFrame) -> pd.DataFrame:
#     columns = ['province', 'station_name', 'time', '_RSSI']
#     if (dataframe.shape[0] < 1):
#         return pd.DataFrame(columns=columns)
#     province = dataframe['province'].iloc[0]
#     station_name = dataframe['station_name'].iloc[0]
#     # must replace this with actual regression
#     regression_res = dataframe['_RSSI'].sum()
#     time = dataframe['time'].max()
#     data = [province, station_name, time, regression_res]
#     return pd.DataFrame(data=data, columns=columns)


def g(df):
    grouped = df.groupby(["province", "station_name"])
    l = []
    for name, group in grouped:
        sumOfRSSI = group['_RSSI'].values.sum()
        time = group['time'].max()
        stationName = name[1]
        province = name[0]
        l.append({
            "station_name": stationName,
            "province": province,
            "_RSSI": sumOfRSSI, 
            "time": time
        })
    return pd.DataFrame(l)


def get_resulting_df_schema():
    return  StructType() \
        .add("province", StringType()) \
        .add("time", TimestampType()) \
        .add("station_name", StringType()) \
        .add("_RSSI", LongType())


if __name__ == "__main__":
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    schema = get_rds_signal_schema()
    signalStream = get_rds_signal_stream(schema)
    _schema = get_resulting_df_schema()

    signalStream.groupBy('province', window(signalStream.time, "5 minutes")) \
        .applyInPandas(g, _schema) \
        .sum('_RSSI') \
        .writeStream \
        .format('console') \
        .outputMode('append') \
        .option("truncate", "false") \
        .start() \
        .awaitTermination()

    # timeWindow = window(signalStream.time, '5 minutes')
    # signalStream \
    #     .groupBy('province', 'station_name', timeWindow) \
    #     .applyInPandas(regression, _schema) \
    #     .writeStream \
    #     .format('console') \
    #     .outputMode('append') \
    #     .option('truncate', 'false') \
    #     .start() \
    #     .awaitTermination()