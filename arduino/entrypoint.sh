#! /bin/bash
if [ "$DISPLAY" != "" ]; then
    echo "DISPLAY=$DISPLAY"
    /usr/local/bin/arduino
else
    echo "Insert the Arduino port (Example: /dev/ttyACM0): "
    read port
    /usr/local/bin/arduino --upload FM_RDS_Radio/FM_RDS_Radio.ino --port $port # <-- This is the X11 application I am testing with. It shows a clock in a Window
fi
echo "Done."