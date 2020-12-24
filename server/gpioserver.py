import curses, time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import threading
from json import dumps
import sys
from bottle import route, run
from bottle import response







print(f'length: {len(sys.argv) > 1}  {sys.argv.__contains__("start-server")}')

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
GPIO.setup(pinGreenLED, GPIO.OUT) 
GPIO.setup(pinBlueLED, GPIO.OUT) 
GPIO.output(pinBlueLED, GPIO.LOW)
GPIO.output(pinGreenLED, GPIO.LOW)


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
State = 1
            #  1 = Not Started
            #  2 = WorkingOut
            #  3 = Paused
            #  4 = Finished

# times
actualStartTime         = time.time()
currentTime             = actualStartTime
lastLoopTime            = currentTime;
chunkRateStartTime      = actualStartTime
totalElapsedTime        = 0.0
lastLastTime            = 0.0
lastLastStepTime        = 0.0
elapsedSinceLastOnState = 0.0

#cLI display stuff and program control stuff
startrow          = 1     #curses lib for STDOUT which row to begin printing
firstcolumn       = 10    #curses - which column to start printing.  offsets are calculated from startrow and startcolumn
loopSleepTime     = 0.05  #how long to pause the main outer loop between reads
decimalPlaces     = 2

def is_not_started():
    return State == 1
    
def is_working_out():
    return State == 2

def is_paused():
    return State == 3    

def is_finished():
    return State == 4

def set_not_started():
    State = 1
    
def set_working_out():
    State = 2
    GPIO.output(pinBlueLED, GPIO.HIGH)

def set_paused():
    State = 3    
    GPIO.output(pinBlueLED, GPIO.LOW)

def set_finished():
    State = 4         

@route('/state')
def returnarray():
    dict= {'TotalElapsedTime': totalElapsedTime, 'distance': distance, 'calories': calories, 'mph':  mph, 'totalCountOnState': totalCountOnState}
    response.content_type = 'application/json'
    return dumps(dict)

def start_server():
    run(host=hostName, port=serverPort, debug=True)

def is_magnet_detected():
    return  GPIO.input(pinHallSensorNorth)  == signal_on or GPIO.input(pinHallSensorSouth) == signal_on

if __name__ == '__main__':
    if startServer == True:
        t = threading.Thread(target=start_server)
        t.start()

    pinWasOn = False
    intitialSteps = 0;
    print(f'Waiting for a few initial steps. intitialSteps: {intitialSteps}, North: {GPIO.input(pinHallSensorNorth)}, South: {GPIO.input(pinHallSensorSouth)}')
    while is_not_started() == True:
        pinDetectsMagnet = is_magnet_detected()
        if(pinDetectsMagnet):
            pinWasOn = True
        if pinDetectsMagnet == signal_off and pinWasOn == True:
            pinWasOn = False
            intitialSteps += 1
        if(intitialSteps > 3):
            set_working_out();
        else:
            time.sleep(loopSleepTime)


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

    
    pinOn = False
    pinOff = True

    while is_working_out() == True or is_paused():

        if is_working_out() == True:
            currentTime      = time.time()
            totalElapsedTime = currentTime - actualStartTime

        totalRate = 0.0 if totalCountOnState == 0.0 else round((60 / totalElapsedTime) * totalCountOnState, 4)
        isHallSensorOn = is_magnet_detected()

        # this means val is now 0 and the previous loop, it was 1
        if isHallSensorOn == False and pinOn == True: 
            GPIO.output(pinGreenLED, GPIO.LOW)
            pinOff = True
            pinOn = False
        
        # this means a whole button press occurred.
        # this prevents multiple counts for a long button press
        if isHallSensorOn == True and pinOff == True:
            GPIO.output(pinGreenLED, GPIO.HIGH)
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

            if elapsedSinceLastOnState > 3.00:
                set_paused()
            else:
                set_working_out()
                timeOfLastOnState = time.time()

            stdscr.addstr(startrow,     firstcolumn + 20, str(totalRate))
            stdscr.addstr(startrow + 1, firstcolumn + 20, str(chunkRate))
            stdscr.addstr(startrow + 2, firstcolumn + 20, str(chunkSize))

            stdscr.addstr(startrow + 5, firstcolumn + 20, str(round(distance, decimalPlaces)))
            stdscr.addstr(startrow + 6, firstcolumn + 20, str(round(mph, decimalPlaces)))
            stdscr.addstr(startrow + 7, firstcolumn + 20, str(round(calories, decimalPlaces)))
            stdscr.addstr(startrow + 3, firstcolumn + 20, str(elapsedSinceLastOnState))
            
            
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
        stdscr.addstr(startrow + 12, firstcolumn + 20, f'steps   :{str(totalCountOnState)}')
        stdscr.addstr(startrow + 15, firstcolumn + 20, f'val     : {str(isHallSensorOn)}')
        
        stdscr.refresh()    # refresh curses UI. This can be adusted based on time (e.g. every 3 seconds)
        time.sleep(loopSleepTime)    # letting this loop run with no sleep() results in 100% CPU usage

    # end the whileloop
    curses.echo()
    curses.endwin()

    GPIO.cleanup()


    print(f'rate per minute : {str(totalRate)}')
    print(f'chunk rate      : {str(chunkRate)}')
    print(f'chunk size      : {str(chunkSize)}')
    print(f'since last step : {str(elapsedSinceLastOnState)}')
    print(f'time            : {str(round(totalElapsedTime, decimalPlaces))}')
    print(f'miles           : {str(round(distance, decimalPlaces))}')
    print(f'mph             : {str(round(mph, decimalPlaces))}')
    print(f'time total      : {round(time.time() - lastLoopTime , decimalPlaces)}')
    print(f'total steps     : {str(totalCountOnState)}')
    print(f'calories        : {str(round(calories, decimalPlaces))}')
    print(f'State           : {str(State)}')

    exit