import serial
from datetime import datetime

# COM port on windows /dev/tty* on Unix system
port = "COM3"

ser = serial.Serial(port, 115200, timeout = 1000)
ser.flushInput()

current_date = datetime.now().strftime('%d-%m-%Y')
filename = f'../logs/arduino-{current_date}.log'
f = open(filename, "w")
f.close() 

while True:
    ser_bytes = ser.readline().decode("utf-8")[:-2] + "\n"
    with open(filename,"a") as f:
        split = ser_bytes.split("FM=")
        if len(split) > 1 and split[1][0] == "0":
            ser_bytes = split[0] + "FM=1" + split[1] 
        if len(ser_bytes) > 5:
            f.write(ser_bytes)
        