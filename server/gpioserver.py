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


GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(pinHallSensorNorth, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(pinHallSensorSouth, GPIO.IN, GPIO.PUD_DOWN)  

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
    metrics = get_metrics(1)
    response.content_type = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'    
    return dumps(metrics)

def start_server():
    run(host=hostName, port=serverPort, debug=True, quiet=True)

paused = False
def pause_for_inactivity():
    global elapsedSinceLastOnStateInSeconds
    global paused
    global currentTime

    currentTime = time.time()
    elapsedSinceLastOnStateInSeconds = currentTime - timeOfLastOnState

    if elapsedSinceLastOnStateInSeconds < 3:
        paused = False
        return False

    paused = True
    return True

timeOfLastOnState = 0.0
def hall_sensor_callback(channel):
    global hallStateOnCount
    global timeOfLastOnState

    hallStateOnCount += 1
    timeOfLastOnState = time.time()

def get_metrics(rounding):
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
            'paused'                             : paused,
            'currentTime'                        : currentTime,               
            'totalElapsedTimeInSeconds'          : round(totalElapsedTimeInSeconds, rounding), 
            'totalElapsedTimeInHours'            : round(totalElapsedTimeInHours, rounding),   
            'elapsedSinceLastOnStateInSeconds'   : round(elapsedSinceLastOnStateInSeconds, rounding),   
            'stepsPerMinute'                     : round(stepsPerMinute, rounding),            
            'distanceInFeet'                     : round(distanceInFeet, rounding),            
            'distanceInMiles'                    : round(distanceInMiles, rounding),           
            'speedInMph'                         : round(speedInMph, rounding),                
            'calories'                           : round(calories, rounding),                  
            'caloriesPerMinute'                  : round(caloriesPerMinute, rounding)
    }  
    return metrics           

def print_summary():
    metrics = get_metrics(4)
    msg = f'''Summary:
    paused                             : {metrics['paused']}
    currentTime                        : {metrics['currentTime']},
    totalElapsedTimeInSeconds          : {metrics['totalElapsedTimeInSeconds']}, 
    totalElapsedTimeInHours            : {metrics['totalElapsedTimeInHours']},  
    elapsedSinceLastOnStateInSeconds   : {metrics['elapsedSinceLastOnStateInSeconds']},  
    stepsPerMinute                     : {metrics['stepsPerMinute']},  
    distanceInFeet                     : {metrics['distanceInFeet']},  
    distanceInMiles                    : {metrics['distanceInMiles']},  
    speedInMph                         : {metrics['speedInMph']},  
    calories                           : {metrics['calories']},  
    caloriesPerMinute                  : {metrics['caloriesPerMinute']}'''
    print(msg);

GPIO.add_event_detect(pinHallSensorNorth, GPIO.RISING, callback=hall_sensor_callback, bouncetime=300) 
GPIO.add_event_detect(pinHallSensorSouth, GPIO.RISING, callback=hall_sensor_callback, bouncetime=300) 

pausedTimeInSeconds = 0.0
timeOfPause = 0.0
if __name__ == '__main__':

    try:
        if startServer == True:
            t = threading.Thread(target=start_server)
            t.start()


        print("Start moving when you're ready...")
        while hallStateOnCount <= 0:
            time.sleep(0.5)

        lastCount = 0
        while True:
            currentTime = time.time()
            
            if pause_for_inactivity():
                print("Paused..")
                pausedTimeInSeconds = 0.0
                timeOfPause = time.time()
                while pause_for_inactivity():
                    time.sleep(1)
                pausedTimeInSeconds = time.time() - timeOfPause
                timeOfPause = 0.0

            if hallStateOnCount > lastCount:
                currentTime = time.time()
                lastCount = hallStateOnCount
                
                totalElapsedTimeInSeconds          = currentTime - actualStartTime - pausedTimeInSeconds
                totalElapsedTimeInHours            = totalElapsedTimeInSeconds / 3600
                

                stepsPerMinute = 0.0 if hallStateOnCount == 0.0 else round((60 / totalElapsedTimeInSeconds) * hallStateOnCount, decimalPlaces)
                distanceInFeet = hallStateOnCount * 4.4
                distanceInMiles = distanceInFeet / 5280
                speedInMph = 0 if totalElapsedTimeInSeconds == 0.00 else round(distanceInMiles / totalElapsedTimeInHours, decimalPlaces)
                
                #260 lb medium resistance/speed 619 calories per hour
                #120 lb medium resistance/speed 286 calories per hour

                #100 - medium - 205 - 238 - 286    
                #150 -        - 307 - 357 - 429     102 + 119 + 143 for each 50lbs
                #200 - medium - 410 - 476 -
                #250 -        -     - 595 - 
                #300 - medium -     - 714 - 

                # basic calorie formula
                # low  intensity = (((weight-100) / 50) * 102) + 205
                # med  intensity = (((weight-100) / 50) * 119) + 205
                # high intensity = (((weight-100) / 50) * 143) + 205
                calories = totalElapsedTimeInSeconds * (0.2)    #12 cals per minute - 120 per hour  - 12/ 160 = per sec
                                                                #6.5 = max
                                                                #2244 =  9mph
                                                                #1,928 joh for 60m at 7  85%
                                                                #1,577	 5mph

                # hardcoding to 260lb person and med intensity for now
                calories = totalElapsedTimeInSeconds * ((((260 - 100) / 50 * 119) + 205) / 3600)
                
                caloriesPerMinute = round((calories / totalElapsedTimeInSeconds) * 60, decimalPlaces)

            print_summary()
            time.sleep(loopSleepTime)    # letting this loop run with no sleep() results in 100% CPU usage
        # end the main whileloop
    except KeyboardInterrupt:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
    exit