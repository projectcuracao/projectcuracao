# sets the BatteryWatchdog Thresholds
# filename: setThreshold.py
# Version 1.0  10/31/13
#
#
#

import sys
import time
import RPi.GPIO as GPIO
import serial

import MySQLdb as mdb
sys.path.append('./pclogging')
sys.path.append('./util')
import pclogging
import util


sys.path.append('/home/pi/ProjectCuracao/main/config')
import conf
# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
        import conflocal as conf
except ImportError:
        import conf




def  setThresholds(source, delay):

	print("setThresholds source:%s" % source)

	time.sleep(delay)
	# blink GPIO LED when it's run
	GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)
        time.sleep(0.5)



	# setup serial port to Arduino

	# interrupt Arduino to start listening

	GPIO.setmode(GPIO.BOARD)
    	GPIO.setup(7, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)	
	GPIO.output(7, False)
	GPIO.output(7, True)
	GPIO.output(7, False)
	

	# Send the STH (Set Thresholds Data) Command
	ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
	# ser.open()
	time.sleep(7.0)

	# send the first "are you there? command - RD - return from Arduino OK"
		
        response = util.sendCommandAndRecieve(ser, "RD")
	print("response=", response);
	
	if (response == "OK\n"):
		print "Good RD Response"
	else:
		print "bad response from RD"
		pclogging.log(pclogging.ERROR, __name__, "RD failed from Pi to BatteryWatchDog")
                ser.close()
		return
	# Read the value

        response = util.sendCommandAndRecieve(ser, "STH")
	print("response=", response);
	
	if (response == "OK\n"):
		print "Good STH Response"
		# set up our time string
		#Dec 26 2009", time = "12:34:56

                #myDateString = time.strftime("%b %d %Y", time.gmtime())
                #myTimeString = time.strftime("%H:%M:%S", time.gmtime())
				
		PI_BATTERY_SHUTDOWN_THRESHOLD = 3.706 # 20%
		PI_BATTERY_STARTUP_THRESHOLD = 3.839 # 30%

		INSIDE_TEMPERATURE_PI_SHUTDOWN_THRESHOLD = 49.33 # 110
		INSIDE_TEMPERATURE_PI_STARTUP_THRESHOLD = 37.78  # 100


		INSIDE_HUMIDITY_PI_SHUTDOWN_THRESHOLD = 98.0 
		INSIDE_HUMIDITY_PI_STARTUP_THRESHOLD = 93.0



		PI_START_TIME = "10:00:00" # UTC
		PI_SHUTDOWN_TIME = "22:30:00" #UTC
		PI_MIDNIGHT_WAKEUP_SECONDS_LENGTH = 3600.0   # one hour

		PI_MIDNIGHT_WAKEUP_THRESHOLD = 3.971   # 60%

		mySendString = "%4.3f, %4.3f, %4.3f, %4.3f, %4.3f, %4.3f,%s,%s, %4.3f, %4.3f, %i\n" % (conf.PI_BATTERY_SHUTDOWN_THRESHOLD, conf.PI_BATTERY_STARTUP_THRESHOLD, conf.INSIDE_TEMPERATURE_PI_SHUTDOWN_THRESHOLD, conf.INSIDE_TEMPERATURE_PI_STARTUP_THRESHOLD, conf.INSIDE_HUMIDITY_PI_SHUTDOWN_THRESHOLD, conf.INSIDE_HUMIDITY_PI_STARTUP_THRESHOLD, conf.PI_START_TIME, conf.PI_SHUTDOWN_TIME, conf.PI_MIDNIGHT_WAKEUP_SECONDS_LENGTH, conf.PI_MIDNIGHT_WAKEUP_THRESHOLD, conf.enableShutdowns)

        	response = util.sendCommandAndRecieve(ser, mySendString)
		if (response == "OK\n"):
			print "Good STH Response"
		else:
			print "bad response from STH second line"
			pclogging.log(pclogging.ERROR, __name__, "STH  second line failed from Pi to BatteryWatchDog")
                	ser.close()
			return

	else:
		print "bad response from STH"
		pclogging.log(pclogging.ERROR, __name__, "STH failed from Pi to BatteryWatchDog")
                ser.close()
		return



	# say goodbye  
        response = util.sendCommandAndRecieve(ser, "GB")
	print("response=", response);
	pclogging.log(pclogging.INFO, __name__, "STH - Thresholds set on Arduino")

	ser.close()
		
