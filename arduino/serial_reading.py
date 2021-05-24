import serial
from datetime import datetime


ser = serial.Serial('/dev/ttyACM0', 115200, timeout = 1000)
ser.flushInput()

current_date = datetime.now().strftime('%d-%m-%Y')
filename = f'../logs/arduino-{current_date}.log'
f = open(filename, "w")
f.close() 

while True:
    ser_bytes = ser.readline().decode("utf-8")[:-2] + "\n"
    with open(filename,"a") as f:
        f.write(ser_bytes)
        