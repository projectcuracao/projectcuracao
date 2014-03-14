# sets the RC time to UTC time on Arduino
# filename: setTime.py
# Version 1.0  10/31/13
#
# contains event routines for data collection from the battery watchdog arduino
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





def  setTime(source, delay):

	print("setTime source:%s" % source)

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
	

	# Send the GD (Get Data) Command
	ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
	#ser.open()
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

        response = util.sendCommandAndRecieve(ser, "ST")
	print("response=", response);
	
	if (response == "OK\n"):
		print "Good ST Response"
		# set up our time string
		#Dec 26 2009", time = "12:34:56

                myDateString = time.strftime("%b %d %Y", time.gmtime())
                myTimeString = time.strftime("%H:%M:%S", time.gmtime())
				
		#myTimeString = time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime())

        	response = util.sendCommandAndRecieve(ser, myDateString)

        	response = util.sendCommandAndRecieve(ser, myTimeString)
		if (response == "OK\n"):
			print "Good ST-2 Response"
		else:
			print "bad response from ST-2 third line"
			pclogging.log(pclogging.ERROR, __name__, "ST-2  second line failed from Pi to BatteryWatchDog")
                	ser.close()
			return

	else:
		print "bad response from ST"
		pclogging.log(pclogging.ERROR, __name__, "ST failed from Pi to BatteryWatchDog")
                ser.close()
		return



	# say goodby  
        response = util.sendCommandAndRecieve(ser, "GB")
	print("response=", response);
	pclogging.log(pclogging.INFO, __name__, "ST - Time Set on Arduino to Pi Time ")

	ser.close()
		
