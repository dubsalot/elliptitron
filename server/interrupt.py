import curses, time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import threading
from json import dumps
import sys
from bottle import route, run
from bottle import response

##startServer = True

pinHallSensorNorth = 12



signal_on = 0
signal_off = 1

stepcount = 0

def hall_sensor_iterrupt(channel):
    global stepcount
    stepcount += 1



GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(pinHallSensorNorth, GPIO.IN, GPIO.PUD_DOWN)

GPIO.add_event_detect(pinHallSensorNorth, GPIO.RISING, callback=hall_sensor_iterrupt, bouncetime=300) 




while True:
    try:
        print(f'stepcount : {stepcount}')
        time.sleep(3)
    except KeyboardInterrupt:
        GPIO.cleanup()
        break

print(f'final stepcount : {stepcount}')