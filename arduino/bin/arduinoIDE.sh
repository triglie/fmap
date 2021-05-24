docker rm ArduinoIDE
docker run --privileged -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY \
       -h $HOSTNAME -v $HOME/.Xauthority:/home/triglie/.Xauthority --name ArduinoIDE youdontneedspotify:ArduinoRadio