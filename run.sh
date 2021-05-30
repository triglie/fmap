#! /bin/bash
DIR="logs"
if [ -d "$DIR" ]; then
  echo "Deleting ${DIR}..."
  sudo rm -r ${DIR}
fi
mkdir logs
docker-compose build kafkastream
docker-compose build kafka-to-es
docker-compose build spark
docker-compose up -d