#!/bin/bash

if [[ -d "setup" ]] 
then 
    rm -r setup/
fi
mkdir -p setup
wget -O ./setup/spark-3.1.1-bin-hadoop2.7.tgz https://downloads.apache.org/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz 