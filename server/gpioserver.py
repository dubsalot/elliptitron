import time, threading, sys
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library

from json import dumps
from bottle import route, run, response

hostName = "192.168.1.85"   # for the web server. electron will call this. will replace with gRPC maybe
serverPort = 9001
jsonEncoding = 'utf-8'
startServer = False
startServer = len(sys.argv) > 1 and sys.argv.__contains__("start-server")
##startServer = True

pinHallSensorNorth = 40
pinHallSensorSouth = 37
pinBlueLED = 38
pinGreenLED = 36


GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(pinHallSensorNorth, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(pinHallSensorSouth, GPIO.IN, GPIO.PUD_DOWN)  
GPIO.setup(pinGreenLED, GPIO.IN, GPIO.PUD_DOWN) 
GPIO.setup(pinBlueLED, GPIO.IN, GPIO.PUD_DOWN) 

#stridesPerMile      = (840 * 10) #leaving this way bc I'm guessing 840 steps per 0.1 miles based on first run
# TRACKED OR CALCULATED METRICS 
distance            = 0.0
calories            = 0.0
caloriesPerMinute   = 0.0
speedInMph          = 0.0
stepsPerMinute      = 0.0
hallStateOnCount    = 0.0
distanceInFeet      = 0.0
distanceInMiles     = 0.0 

# times
actualStartTime                           = time.time()
currentTime                               = actualStartTime
totalElapsedTimeInSeconds                 = 0.0
totalElapsedTimeInHours                   = 0.0
elapsedSinceLastOnStateInSeconds          = 0.0

#cLI display stuff and program control stuff
loopSleepTime     = 1     #how long to pause the main outer loop between reads
decimalPlaces     = 1

     

@route('/state')
def returnarray():
    metrics = get_metrics()
    response.content_type = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'    
    return dumps(metrics)

def start_server():
    run(host=hostName, port=serverPort, debug=True, quiet=True)

timeOfLastOnState = 0
def hall_sensor_callback(channel):
    global hallStateOnCount
    global timeOfLastOnState

    hallStateOnCount += 1
    timeOfLastOnState = time.time()

def get_metrics():
    global currentTime               
    global totalElapsedTimeInSeconds 
    global totalElapsedTimeInHours   
    global elapsedSinceLastOnStateInSeconds   
    global stepsPerMinute            
    global distanceInFeet            
    global distanceInMiles           
    global speedInMph                
    global calories                  
    global caloriesPerMinute
    metrics = {
            'currentTime'               : currentTime,               
            'totalElapsedTimeInSeconds' : totalElapsedTimeInSeconds, 
            'totalElapsedTimeInHours'   : totalElapsedTimeInHours,   
            'elapsedSinceLastOnState'   : elapsedSinceLastOnStateInSeconds,   
            'stepsPerMinute'            : stepsPerMinute,            
            'distanceInFeet'            : distanceInFeet,            
            'distanceInMiles'           : distanceInMiles,           
            'speedInMph'                : speedInMph,                
            'calories'                  : calories,                  
            'caloriesPerMinute'         : caloriesPerMinute
    }  
    return metrics           

def print_summary():
    metrics = get_metrics()
    msg = f'''Summary:
    currentTime               : {metrics['currentTime']},
    totalElapsedTimeInSeconds : {metrics['totalElapsedTimeInSeconds']}, 
    totalElapsedTimeInHours   : {metrics['totalElapsedTimeInHours']},  
    elapsedSinceLastOnState   : {metrics['elapsedSinceLastOnState']},  
    stepsPerMinute            : {metrics['stepsPerMinute']},  
    distanceInFeet            : {metrics['distanceInFeet']},  
    distanceInMiles           : {metrics['distanceInMiles']},  
    speedInMph                : {metrics['speedInMph']},  
    calories                  : {metrics['calories']},  
    caloriesPerMinute         : {metrics['caloriesPerMinute']}'''
    print(msg);

GPIO.add_event_detect(pinHallSensorNorth, GPIO.RISING, callback=hall_sensor_callback, bouncetime=300) 
GPIO.add_event_detect(pinHallSensorSouth, GPIO.RISING, callback=hall_sensor_callback, bouncetime=300) 

if __name__ == '__main__':

    try:
        if startServer == True:
            t = threading.Thread(target=start_server)
            t.start()


        while True:
            currentTime                        = time.time()
            totalElapsedTimeInSeconds          = currentTime - actualStartTime
            totalElapsedTimeInHours            = totalElapsedTimeInSeconds / 3600
            elapsedSinceLastOnStateInSeconds   = currentTime - timeOfLastOnState

            stepsPerMinute = 0.0 if hallStateOnCount == 0.0 else round((60 / totalElapsedTimeInSeconds) * hallStateOnCount, decimalPlaces)
            distanceInFeet = hallStateOnCount * 2
            distanceInMiles = distanceInFeet / 5280
            speedInMph = 0 if totalElapsedTimeInSeconds == 0.00 else round(distanceInMiles / totalElapsedTimeInHours, decimalPlaces)
            calories = totalElapsedTimeInSeconds * (0.2)    #12 cals per minute - 120 per hour  - 12/ 160 = per sec
                                                            #6.5 = max
                                                            #2244 =  9mph
                                                            #1,928 joh for 60m at 7  85%
                                                            #1,577	 5mph

            caloriesPerMinute = round((calories / totalElapsedTimeInSeconds) * 60, decimalPlaces)

            print_summary()
            time.sleep(loopSleepTime)    # letting this loop run with no sleep() results in 100% CPU usage
        # end the main whileloop
    except KeyboardInterrupt:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
    exit