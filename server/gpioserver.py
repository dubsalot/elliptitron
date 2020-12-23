import curses, time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import sleep     # Import the sleep function from the time module
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json

hostName = "localhost"   # for the web server. electron will call this. will replace with gRPC maybe
serverPort = 9001
jsonEncoding = 'utf-8'

pinHallSensor = 40
pinBlueLED = 38
pinGreenLED = 36
pinStepIndicatorLED = 37

signal_on = 0
signal_off = 1
isGreenOn = 0
isBlueOn = 0
pinOn = False
pinOff = True

GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(pinHallSensor, GPIO.IN, GPIO.PUD_DOWN) 
GPIO.setup(pinBlueLED, GPIO.IN, GPIO.PUD_DOWN) 
GPIO.setup(pinGreenLED, GPIO.IN, GPIO.PUD_DOWN) 
GPIO.setup(pinStepIndicatorLED, GPIO.OUT, initial=GPIO.LOW)


# used to account for multiple readings of On during one on-state
onStateThreshold = 0.05
timeOfLastOnState = 0.0


countOnStates = 0
chunkSize = 5
chunkRate = 0.0



# TRACKED OR CALCULATED METRICS 
distance = 0.0
stridesPerMile = 63360 / 22
calories = 0.0
mph = 0
totalRate = 0.0
totalCountOnState = 0.0

# times
startTime               = time.time()
currentTime             = startTime
lastLoopTime            = currentTime;
chunkRateStartTime      = startTime
totalElapsedTime        = 0.0
lastLastTime            = 0.0
lastLastStepTime        = 0.0
elapsedSinceLastOnState = 0.0


isGreenOn      = GPIO.input(pinGreenLED)
isBlueOn       = GPIO.input(pinBlueLED)
isHallSensorOn = GPIO.input(pinHallSensor)


#cLI display stuff and program control stuff
startrow          = 1     #curses lib for STDOUT which row to begin printing
firstcolumn       = 10    #curses - which column to start printing.  offsets are calculated from startrow and startcolumn
loopSleepTime     = 0.05  #how long to pause the main outer loop between reads
sleepTimeForStart = 4     #first wait loop in the program to wait for blue LED to turn on
decimalPlaces     = 2

while isBlueOn == 0:
    print(f'Waiting for blue light. Checking again in {sleepTimeForStart} seconds.')
    print(f'pin read for HallSensor ---------> {GPIO.input(pinHallSensor)}')
    print(f'pin read for GreenLED   ---------> {GPIO.input(pinGreenLED)}')
    print(f'pin read for BlueLED          ---> {GPIO.input(pinBlueLED)}')
    print(f'pin read for StepIndicatorLED ---> {GPIO.input(pinStepIndicatorLED)}')
    time.sleep(sleepTimeForStart)
    isBlueOn = GPIO.input(pinBlueLED)


#init curses
stdscr = curses.initscr()

#print labels
stdscr.addstr(startrow,     firstcolumn, "rate per minute :")
stdscr.addstr(startrow + 1, firstcolumn, "chunk rate      :")
stdscr.addstr(startrow + 2, firstcolumn, "chunk size      :")        
stdscr.addstr(startrow + 3, firstcolumn, "since last step :")
stdscr.addstr(startrow + 4, firstcolumn, "time            :")
stdscr.addstr(startrow + 5, firstcolumn, "miles           :")
stdscr.addstr(startrow + 6, firstcolumn, "mph             :")
stdscr.addstr(startrow + 7, firstcolumn, "calories        :")

isGreenOn = GPIO.input(pinGreenLED)
isBlueOn = GPIO.input(pinBlueLED)


class GPIOServer(BaseHTTPRequestHandler):
    def do_GET(self):
        dict= {'TotalElapsedTime': totalElapsedTime}
        resp = json.dumps(dict)
        self.send_response(200)
        self.send_header("Content-type", "text/text")
        self.end_headers()
        self.wfile.write(bytes(resp, jsonEncoding))
        self.wfile.flush()
        self.wfile.close()



def start_server():
    # Setup stuff here...
    webServer = HTTPServer((hostName, serverPort), GPIOServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.start()


    while isBlueOn == 1:
        currentTime      = time.time()
        totalElapsedTime = currentTime - startTime
        totalRate        = 0.0 if totalCountOnState == 0.0 else round((60 / totalElapsedTime) * totalCountOnState, 4)
        
        isHallSensorOn = GPIO.input(pinHallSensor)
        isGreenOn      = GPIO.input(pinGreenLED)
        isBlueOn       = GPIO.input(pinBlueLED)

        #this means val is now 0 and the previous loop, it was 1
        if isHallSensorOn == signal_off and pinOn == True: 
            GPIO.output(pinStepIndicatorLED, GPIO.LOW)
            pinOff = True
            pinOn = False
        
        #this means a whole button press occurred.
        #this prevents multiple counts for a long button press
        if isHallSensorOn == signal_on and pinOff == True:
            GPIO.output(pinStepIndicatorLED, GPIO.HIGH)
            pinOn = True
            pinOff = False
                
        
            elapsedSinceLastOnState = round(0.0 if timeOfLastOnState == 0.0 else currentTime - timeOfLastOnState, decimalPlaces)
            onsPerMinute = 0.0 if elapsedSinceLastOnState <= 0 else round(60 / elapsedSinceLastOnState, decimalPlaces)
            countOnStates = countOnStates + 1
            totalCountOnState = totalCountOnState + 1
            distance = totalCountOnState / stridesPerMile
            mph = 0 if totalElapsedTime == 0.00 else round(distance / (totalElapsedTime / 3600), decimalPlaces)

            #12 cals per minute - 120 per hour  - 12/ 160 = per sec
            calories = totalElapsedTime * (0.2)
                                                        #6.5 = max
                                                        #2244 =  9mph
                                                        #1,928 joh for 60m at 7  85%
                                                        #1,577	 5mph

            stdscr.addstr(startrow,     firstcolumn + 20, str(totalRate))
            stdscr.addstr(startrow + 1, firstcolumn + 20, str(chunkRate))
            stdscr.addstr(startrow + 2, firstcolumn + 20, str(chunkSize))

            stdscr.addstr(startrow + 5, firstcolumn + 20, str(round(distance, decimalPlaces)))
            stdscr.addstr(startrow + 6, firstcolumn + 20, str(round(mph, decimalPlaces)))
            stdscr.addstr(startrow + 7, firstcolumn + 20, str(round(calories, decimalPlaces)))
            stdscr.addstr(startrow + 3, firstcolumn + 20, str(elapsedSinceLastOnState))
            
            timeOfLastOnState = time.time()
        # end if val = 1

        
        if countOnStates >= chunkSize:
            if chunkRateStartTime != 0.0:
                timeFor5Steps = time.time() - chunkRateStartTime
                chunkRate = 0.0 if chunkRateStartTime == 0.0 else round(((60 / (time.time() - chunkRateStartTime)) * chunkSize), decimalPlaces)
            countOnStates = 0
            chunkRateStartTime = time.time()      #reset the chunk counter  
        # end  if countOnStates >= chunkSize

        stdscr.addstr(startrow + 3, firstcolumn + 20, str(elapsedSinceLastOnState))    
        stdscr.addstr(startrow + 4, firstcolumn + 20, str(round(totalElapsedTime, decimalPlaces)))

        stdscr.addstr(startrow + 9,  firstcolumn + 20, f'green   : {str(isGreenOn)}')
        stdscr.addstr(startrow + 10, firstcolumn + 20, f'blue    : {str(isBlueOn)}')
        stdscr.addstr(startrow + 12, firstcolumn + 20, f'steps   :{str(totalCountOnState)}')

        stdscr.addstr(startrow + 15, firstcolumn + 20, f'val     : {str(isHallSensorOn)}')
        stdscr.addstr(startrow + 16, firstcolumn + 20, f'stepPin : {GPIO.input(pinStepIndicatorLED)}')

        stdscr.refresh()    # refresh curses UI. This can be adusted based on time (e.g. every 3 seconds)
        time.sleep(loopSleepTime)    # letting this loop run with no sleep() results in 100% CPU usage

    # end the whileloop
    curses.echo()
    curses.endwin()

    GPIO.cleanup()


    print(f'green           : {str(isGreenOn)}')
    print(f'blue            : {str(isBlueOn)}')
    print(f'rate per minute : {str(totalRate)}')
    print(f'chunk rate      : {str(chunkRate)}')
    print(f'chunk size      : {str(chunkSize)}')
    print(f'since last step : {str(elapsedSinceLastOnState)}')
    print(f'time            : {str(round(totalElapsedTime, decimalPlaces))}')
    print(f'miles           : {str(round(distance, decimalPlaces))}')
    print(f'mph             : {str(round(mph, decimalPlaces))}')
    print(f'time total      : {round(time.time() - lastLoopTime , decimalPlaces)}')
    print(f'total steps     : {str(totalCountOnState)}')
    print(f'calories     : {str(round(calories, decimalPlaces))}')

    exit