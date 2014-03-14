# reset watchdog time  on Arudino
# filename:  sendWatchDogTimer.py 
# Version 1.0 11/29/13 
#
# contains reseet the watchdog on the Arduino 
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

# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf


def  sendWatchDogTimer(source, delay,ser):

	print("sendWatchDogTimer source:%s" % source)

	time.sleep(delay)

        response = util.sendCommandAndRecieve(ser, "WD")
	print("response=", response);
	

	if (len(response) > 0):

		print("WD success")
		# pclogging.log(pclogging.INFO, __name__, "Watchdog Timer Reset on Arduino" )
	else:
		# system setup

		pclogging.log(pclogging.ERROR, __name__, "WD failed from Pi to BatteryWatchDog")

	


		

