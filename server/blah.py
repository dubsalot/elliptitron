import curses, time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import threading
from json import dumps
import sys
from bottle import route, run
from bottle import response


pinBlueLED = 38
pinGreenLED = 36


signal_on = 0
signal_off = 1

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

pinHallSensorNorth = 40
pinHallSensorSouth = 37

GPIO.setup(pinHallSensorNorth, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(pinHallSensorSouth, GPIO.IN, GPIO.PUD_DOWN) 

GPIO.setup(pinGreenLED, GPIO.OUT) 
GPIO.setup(pinBlueLED, GPIO.OUT) 

GPIO.output(pinBlueLED, GPIO.LOW)
GPIO.output(pinGreenLED, GPIO.LOW)

print(GPIO.input(pinBlueLED))
print(GPIO.input(pinGreenLED))
