
# gets the RC time from UTC time on Arduino
# filename: getTime.py
# Version 1.0  03/09/14 
#
# contains event routines for data collection from the battery watchdog arduino
#
#

import sys
import time
import RPi.GPIO as GPIO
import serial
import subprocess

sys.path.append('./pclogging')
sys.path.append('./util')
import pclogging
import util





def  getTime(source, delay):

	print("getTime source:%s" % source)

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

        response = util.sendCommandAndRecieve(ser, "RT")
	print("response=", response);

	datecommand = "date -s '" + response + "'"
	print datecommand
	output = subprocess.check_output (datecommand,shell=True, stderr=subprocess.STDOUT )



	# say goodby  
        response = util.sendCommandAndRecieve(ser, "GB")
	print("response=", response);
	pclogging.log(pclogging.INFO, __name__, "RT - Time Set on Pi to Arduino Time ")

	ser.close()
		
