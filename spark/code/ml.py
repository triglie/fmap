from pyspark.sql import SparkSession 
from pyspark.sql.functions import from_json, col, create_map, unix_timestamp
from pyspark.sql.types import *
from pyspark.sql import DataFrame
from pyspark.ml.regression import LinearRegression 
from pyspark.ml.linalg import Vectors, VectorUDT, DenseVector
from pyspark.sql import Row
import datetime

def clean_raw_data(raw: DataFrame) -> DataFrame:
  time_format = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
  return raw.select(
    col('@timestamp').cast('timestamp'), 
    col('FM'), 
    col('PI'), 
    col('RSSI').cast('long'), 
    col('coords'), 
    col('province'), 
    col('station_name')) \
  .withColumn('milliseconds', unix_timestamp('@timestamp', format=time_format))

def get_data_as_libsvm(dataframe: DataFrame) -> LabeledPoint:
  encode = lambda row: LabeledPoint(row['RSSI'], [row['milliseconds']])
  return dataframe.rdd.map(encode)

def attach_feature_as_vectors(dataframe) -> DataFrame:
  to_vector = lambda millis: Vectors.dense([millis])
  milliseconds_to_vec = udf(to_vector, VectorUDT())
  return dataframe.withColumn('millis_vec', milliseconds_to_vec(dataframe.milliseconds))

def get_linear_regression_model(training_set):
  lr = LinearRegression(
    maxIter=10, 
    regParam=0.3, 
    elasticNetParam=0.8, 
    featuresCol='millis_vec', 
    labelCol='RSSI'
  )
  return lr.fit(training_set)

spark = SparkSession \
  .builder \
    .appName('rssi_signal_prediction') \
      .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
raw_data = spark.createDataFrame(js)
df = clean_raw_data(raw_data)
# training = get_data_as_libsvm(df)
training = attach_feature_as_vectors(df)

lastSignalMilliseconds = training.agg({'milliseconds': 'max'}).collect()[0]['max(milliseconds)']
# print(lastSignalMilliseconds)

pr1 = lastSignalMilliseconds + (60000 * 1)
pr2 = lastSignalMilliseconds + (60000 * 2)
pr3 = lastSignalMilliseconds + (60000 * 3)
pr4 = lastSignalMilliseconds + (60000 * 4)
pr5 = lastSignalMilliseconds + (60000 * 5)

test = spark.createDataFrame(
  [(datetime.datetime(2021, 5, 28, 6, 25, 56, 630000), '92.2', 'null', '-114', '38.1121,13.3366', 'Palermo', 'Radio Studio Sicar', pr1, Vectors.dense(pr1))], 
  ["@timestamp", "FM", "PI", "RSSI", "coords", "province", "station_name", "milliseconds", "millis_vec"])

# rowToPredict = Row(millis_vec=Vectors.dense([pr1]))
# rowToPredict = Row(millis_vec=DenseVector([pr1]))
print(lrModel.predict(test.head))
# linear_model = get_linear_regression_model(training)
# print("Coefficients: %s" % str(linear_model.coefficients))
# print("Intercept: %s" % str(linear_model.intercept))
# print(summary)
# print(training.head().millis_vec)
# print(lrModel.predict(training.head().millis_vec))
training.head()
# print(df.milliseconds.max())