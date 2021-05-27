FROM openjdk:8-jre

LABEL maintainer="ziobenzon@triglie.com"

ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.1.1
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH

ADD setup/spark-${SPARK_VERSION}-bin-hadoop2.7.tgz /opt

RUN apt-get update && apt-get -y install bash python3 python3-pip netcat

RUN pip3 install pyspark numpy elasticsearch
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop2.7 ${SPARK_DIR} 

ADD code/*  /opt/tap/
ADD spark-manager.sh $SPARK_DIR/bin/spark-manager

WORKDIR ${SPARK_DIR}
ENTRYPOINT [ "spark-manager" ]