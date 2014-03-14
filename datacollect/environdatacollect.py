# environmental data collection events
# filename: environdatacollect.py
# Version 1.4 02/17/14
#
# contains event routines for data collection
#
#



import sys
import time

import RPi.GPIO as GPIO
import re
import math
import subprocess
import serial

sys.path.append('./pclogging')
sys.path.append('./util')

sys.path.append('/home/pi/ProjectCuracao/main/config')

# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf


import util
import pclogging

from luxmeter import Luxmeter
from Adafruit_BMP085 import *

from Adafruit_I2C import Adafruit_I2C
from PC_BM017CS import BM017

import MySQLdb as mdb

def  environdatacollect(source, delay):

	print("environdatacollect source:%s" % source)

	# delay to not "everything happen at once"
	time.sleep(delay)
	# blink GPIO LED when it's run
	# double blink
	GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)
        time.sleep(0.5)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)

	# now read in all the required data
	# Inside Temperature
	# Barometric Pressure

        # Initialise the BMP085 and use STANDARD mode (default value)
        # bmp = BMP085(0x77, debug=True)
        # bmp = BMP085(0x77)

        # To specify a different operating mode, uncomment one of the following:
        # bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
        # bmp = BMP085(0x77, 1)  # STANDARD Mode
        # bmp = BMP085(0x77, 2)  # HIRES Mode
        bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode



	pressure = -1000.0 # bad data
	insidetemperature =-1000.0
        try:
               pressure = bmp.readPressure()/100.0
               insidetemperature = bmp.readTemperature()

        except IOError as e:
               print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
               print "Unexpected error:", sys.exc_info()[0]
               raise


	# Inside Humidity

        Oldinsidehumidity = -1000.0 # bad data
        insidehumidity = -1000.0 # bad data
        try:
                maxCount = 20
                count = 0
                while (count < maxCount):
                    output = subprocess.check_output(["/home/pi/ProjectCuracao/main/hardware/Adafruit_DHT_MOD", "22", "23"]);
                    print "count=", count
                    print output
                    # search for humidity printout
                    matches = re.search("Hum =\s+([0-9.]+)", output)

                    if (not matches):
                          count = count + 1
                          time.sleep(3.0)
                          continue
                    Oldinsidehumidity = float(matches.group(1))
                    count = maxCount

		# now do it again.  Throw out the higher value (get rid of high spikes)	

		time.sleep(1.0)
                maxCount = 20
                count = 0
                while (count < maxCount):
                    output = subprocess.check_output(["/home/pi/ProjectCuracao/main/hardware/Adafruit_DHT_MOD", "22", "23"]);
                    print "count=", count
                    print output
                    # search for humidity printout
                    matches = re.search("Hum =\s+([0-9.]+)", output)

                    if (not matches):
                          count = count + 1
                          time.sleep(3.0)
                          continue
                    insidehumidity = float(matches.group(1))
                    count = maxCount

		    if (Oldinsidehumidity < insidehumidity):
		 	  insidehumidity = Oldinsidehumidity

        except IOError as e:
                 print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
                 print "Unexpected error:", sys.exc_info()[0]
                 raise

		

	# setup serial port to Arduino

	# interrupt Arduino to start listening

	
	GPIO.setmode(GPIO.BOARD)	
	GPIO.setup(7, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
	GPIO.output(7, False)
	GPIO.output(7, True)
	GPIO.output(7, False)
	

	# Outside Temperature


	# read the latest value from the Arduino


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

        response = util.sendCommandAndRecieve(ser, "GTH")
	print("response=", response);
	


	# stuff the values into variables
	splitList = response.split(',')
	print(splitList)	

	if (len(splitList) == 2):
		outsidetemperature = float(splitList[0])
        	outsidehumidity = float(splitList[1])
	else:
		print "bad response from GTH"
		# system setup

		pclogging.log(pclogging.ERROR, __name__, "GTH failed from Pi to BatteryWatchDog")

		# say goodby  
        	response = util.sendCommandAndRecieve(ser, "GB")
		print("response=", response);
		ser.close()
		return
	


	print("response=", response);

	# say goodby  
        response = util.sendCommandAndRecieve(ser, "GB")
	print("response=", response);

	ser.close()


	# Luminosity
	luminosity = -1000.0 # bad data
        try:
              oLuxmeter=Luxmeter()

              luminosity = oLuxmeter.getLux()
        except IOError as e:
              print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
              print "Unexpected error:", sys.exc_info()[0]
              raise

	# Fan State
	
	# read from fan state file
        try:
		f = open("./state/fanstate.txt", "r")
		tempString = f.read()
        	f.close()
        	fanstate = int(tempString)
	except IOError as e:
		fanstate = 0

	print "fanstate=", fanstate

	# now find our colors

	bm017 = BM017(True)

	red_color = 0
	blue_color = 0
	green_color = 0
	clear_color = 0
	Gain = 0x00
	IntegrationTime = 0xC0

	bm017.disableDevice()
	bm017.setIntegrationTimeAndGain(IntegrationTime, Gain)


	
	if (bm017.isBM017There()):
		bm017.getColors()
		red_color = bm017.red_color
		blue_color = bm017.blue_color
		green_color = bm017.green_color
		clear_color = bm017.clear_color

	# now we have the data, stuff it in the database

	try:
		print("trying database")
    		con = mdb.connect('localhost', 'root', conf.databasePassword, 'ProjectCuracao');

    		cur = con.cursor()
		print "before query"

		query = 'INSERT INTO environmentaldata(TimeStamp, InsideTemperature, InsideHumidity, OutsideTemperature, OutsideHumidity, BarometricPressure, Luminosity, FanState, Red_Color, Blue_Color, Green_Color, Clear_Color, Gain, IntegrationTime) VALUES(UTC_TIMESTAMP(), %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %i, %i, %i, %i, %i, %i, %i)' % (insidetemperature, insidehumidity, outsidetemperature, outsidehumidity, pressure, luminosity, fanstate, red_color, blue_color, green_color, clear_color, Gain, IntegrationTime) 
		print("query=%s" % query)

		cur.execute(query)
	
		con.commit()
		
	except mdb.Error, e:
  
    		print "Error %d: %s" % (e.args[0],e.args[1])
    		con.rollback()
    		#sys.exit(1)
    
	finally:    
       		cur.close() 
        	con.close()

		del cur
		del con

