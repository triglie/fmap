DIR="./logs"
if [ -d "$DIR" ]; then
  echo "Deleting ${DIR}..."
  sudo rm -R ${DIR}
fi
docker-compose build kafkastream
docker-compose build kafka-to-es
docker-compose build spark
docker-compose up -d