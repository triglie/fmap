FROM openjdk:11

RUN apt update && apt upgrade -y \
    && apt install g++ -y \
    && apt install -y x11-apps \
    && apt install libxtst6 -y

ADD ./arduino-1.8.13-linux64.tar.xz /home

COPY ./FM_RDS_Radio /home/arduino-1.8.13/examples/FM_RDS_Radio
COPY ./libraries/Radio /home/arduino-1.8.13/libraries/Radio

RUN /home/arduino-1.8.13/install.sh

RUN groupadd -g 1000 triglie
RUN useradd -d /home/triglie -s /bin/bash -m triglie -u 1000 -g 1000
USER triglie
ENV HOME /home/triglie

COPY ./.arduino15 /home/triglie/.arduino15

WORKDIR /home/arduino-1.8.13/examples

COPY entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"] 