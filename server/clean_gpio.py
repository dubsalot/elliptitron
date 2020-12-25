import curses, time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import threading
from json import dumps
import sys
from bottle import route, run
from bottle import response

hostName = "localhost"   # for the web server. electron will call this. will replace with gRPC maybe
serverPort = 9001
jsonEncoding = 'utf-8'
startServer = False
startServer = len(sys.argv) > 1 and sys.argv.__contains__("start-server")
##startServer = True

pinHallSensorNorth = 40
pinHallSensorSouth = 37
pinBlueLED = 38
pinGreenLED = 36


signal_on = 0
signal_off = 1

pinOn = False
pinOff = True

GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(pinHallSensorNorth, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(pinHallSensorSouth, GPIO.IN, GPIO.PUD_DOWN)  
GPIO.setup(pinGreenLED, GPIO.IN, GPIO.PUD_DOWN) 
GPIO.setup(pinBlueLED, GPIO.IN, GPIO.PUD_DOWN) 

while True:
    try:
        print(f'green : {GPIO.input(pinGreenLED)}')
        print(f'blue  : {GPIO.input(pinBlueLED)}')
        time.sleep(5)
    except KeyboardInterrupt:
        GPIO.cleanup()