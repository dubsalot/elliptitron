import curses, time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import sleep     # Import the sleep function from the time module


signalPin = 40
switchPin = 8

GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
# GPIO.setup(switchPin, GPIO.OUT, initial=GPIO.LOW)   # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(signalPin, GPIO.IN, GPIO.PUD_DOWN) 


# used to account for multiple readings of On during one on-state
onStateThreshold = 0.05
timeOfLastOnState = 0.0
startTime = time.time()
currentTime = startTime
countOnStates = 0

chunkSize = 5
chunkRateStartTime = startTime
chunkRate = 0.0

decimalPlaces = 2

pinOn = False
pinOff = True    #

lastLastTime = 0.0
lastLastStepTime = 0.0

elapsedSinceLastOnState = 0.0
totalElapsedTime = 0.0
totalCountOnState = 0.0
startrow = 1
firstcolumn = 10
distance = 0.0
stridesPerMile = 63360 / 22



while True:
    currentTime = time.time()
    totalElapsedTime = currentTime - startTime
    
    totalRate = 0.0 if totalCountOnState == 0.0 else round((60 / totalElapsedTime) * totalCountOnState, 4)
    
    if (currentTime - timeOfLastOnState ) > 15.0 and timeOfLastOnState != 0.0:
        break

    val = GPIO.input(signalPin)

    #this means val is now 0 and the previous loop, it was 1
    if val == 0 and pinOn == True: 
        pinOff = True
        pinOn = False
    
    #this means a whole button press occurred.
    #this prevents multiple counts for a long button press
    if val == 1 and pinOff == True:
        pinOn = True
        pinOff = False
        
        
        
        elapsedSinceLastOnState = round(0.0 if timeOfLastOnState == 0.0 else currentTime - timeOfLastOnState, decimalPlaces)
        onsPerMinute = 0.0 if elapsedSinceLastOnState <= 0 else round(60 / elapsedSinceLastOnState, decimalPlaces)
            
        # default threshold is 0.05. this accounts for the fast loop
        #if elapsedSinceLastClick > onStateThreshold :
        countOnStates = countOnStates + 1
        totalCountOnState = totalCountOnState + 1
        distance = totalCountOnState / stridesPerMile
        mph = 0 if totalElapsedTime == 0.00 else round(distance / (totalElapsedTime / 3600), 2)

        # stdscr.addstr(startrow,     firstcolumn + 20, str(totalRate))
        # stdscr.addstr(startrow + 1, firstcolumn + 20, str(chunkRate))
        # stdscr.addstr(startrow + 2, firstcolumn + 20, str(chunkSize))

        # stdscr.addstr(startrow + 5, firstcolumn + 20, str(round(distance, 2)))
        # stdscr.addstr(startrow + 6, firstcolumn + 20, str(round(mph, 2)))
        
                
               


        #print("totalRate: ", totalRate, "   OPM: ", onsPerMinute, "    chunkRate: ", chunkRate, " -- sinceLastClick: ", elapsedSinceLastOnState)
        # end if elapsedSinceLastClick > onStateThreshold

        # stdscr.addstr(startrow + 3, firstcolumn + 20, str(elapsedSinceLastOnState))

        print ("")
        timeOfLastOnState = time.time()
    # end if val = 1

    
    if countOnStates >= chunkSize:
        if chunkRateStartTime != 0.0:
            timeFor5Steps = time.time() - chunkRateStartTime
            chunkRate = 0.0 if chunkRateStartTime == 0.0 else round(((60 / (time.time() - chunkRateStartTime)) * chunkSize), decimalPlaces)
        countOnStates = 0
        chunkRateStartTime = time.time()      #reset the chunk counter  
    # end  if countOnStates >= chunkSize

    # tet = round(totalElapsedTime,2)
    # if abs(tet-lastLastTime) >= 0.01:
        
    #     lastLastTime = tet
    # stdscr.addstr(startrow + 3, firstcolumn + 20, str(elapsedSinceLastOnState))    
    # stdscr.addstr(startrow + 4, firstcolumn + 20, str(round(totalElapsedTime,2)))        
    
    # stdscr.refresh()
    time.sleep(0.05)

# end the whileloop
curses.echo()
curses.endwin()
exit