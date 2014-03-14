# monitors the system and executes actions 
# filename: monitorSystem.py 
# Version 1.0  11/11/13 
#
# contains the main system monitoring and action loops 
#
#

import sys
import time
import RPi.GPIO as GPIO
import serial
import subprocess
import re

import MySQLdb as mdb
sys.path.append('./pclogging')
sys.path.append('./util')
sys.path.append('./hardware')

from Adafruit_BMP085 import *
from Subfact_ina219 import INA219
import hardwareactions
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



def  monitorSystem(source, delay):

	print("monitorSystem source:%s" % source)

	time.sleep(delay)
	# blink GPIO LED when it's run
	GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        time.sleep(1.5)
        GPIO.output(22, True)

	# Fan control code - turning fan on

	# grab current latest conditions.

	# read inside temp/hum live

	# grab last outside temp from database

	
	
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



	insidetemperature =-1000.0
        try:
               insidetemperature = bmp.readTemperature()

        except IOError as e:
               print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
               print "Unexpected error:", sys.exc_info()[0]
               raise


	# Inside Humidity

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
                    insidehumidity = float(matches.group(1))
                    count = maxCount



        except IOError as e:
                 print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
                 print "Unexpected error:", sys.exc_info()[0]
                 raise


	# now get the latest outside information


	try:
      		print("trying database")
       		db = mdb.connect('localhost', 'root', 'bleh0101', 'ProjectCuracao');
		
       		cursor = db.cursor()


		query = "SELECT OutsideTemperature, OutsideHumidity FROM batterywatchdogdata ORDER BY ID DESC LIMIT 1"
              	cursor.execute(query)
               	result = cursor.fetchone()
		print result
		outsidetemperature = result[0]
		outsidehumidity = result[1]


        except mdb.Error, e:
		
        	print "Error %d: %s" % (e.args[0],e.args[1])

        finally:
		
        	cursor.close()
               	db.close()
	
       		del cursor
       		del db

        ina44 = INA219(0x44)
        solarvoltage = ina44.getBusVoltage_V()




	print "state:"
	print "   insidetemperature = \t\t", insidetemperature
	print "   insidehumidity = \t\t", insidehumidity
	print "   outsidetemperature = \t", outsidetemperature
	print "   outsidehumidity = \t\t", outsidehumidity
	print "   solarvoltage = \t\t%3.2f" %  solarvoltage
	
	
	print "WARNING:solar overidden to 6.0 for testing"
	solarvoltage = 6.0

	# now do monitor brain calculations

	fanOn = hardwareactions.returnFanState()

	
	if (fanOn == False): 
		# fan is off, look at turning on

		# fan is not on, so let's look to see if we should turn it on

		# check to see if solar voltage is > 4.0 on pi



		if (solarvoltage > 4.0):
			print "solar voltage > 4.0"
		
			#if temp inside is too hot and outside is cooler, turn fan on

			if ((insidetemperature > conf.FAN_ON_TEMPERATURE) and (insidetemperature >= outsidetemperature)):
				hardwareactions.setfan(True)	
				pclogging.log(pclogging.INFO, __name__, "fanON insidetemp> FAN_ON_TEMPERATURE and inside > outside")
				# send an email that the fan turned on
				message = "Fan turning ON:  State: ot:%3.2f it:%3.2f oh:%3.2f ih:%3.2f sv:%3.2f" % (outsidetemperature, insidetemperature, outsidehumidity, insidehumidity, solarvoltage)
				util.sendEmail("test", message, "ProjectCuracao Fan ON(TMP)",  conf.notifyAddress,  conf.fromAddress, "");
				print "monitorSystems Turning FAN ON" 

			#if humidity inside is too high and outside is less, turn fan on

			if ((insidehumidity > conf.FAN_ON_HUMIDITY) and (insidehumidity >  outsidehumidity)):
				hardwareactions.setfan(True)	
				pclogging.log(pclogging.INFO, __name__, "fanON insidehumid> FAN_ON_HUMIDITY  and inside > outside")
				message = "Fan turning ON:  State: ot:%3.2f it:%3.2f oh:%3.2f ih:%3.2f sv:%3.2f" % (outsidetemperature, insidetemperature, outsidehumidity, insidehumidity, solarvoltage)
				util.sendEmail("test",message, "ProjectCuracao Fan ON(HUM)",  conf.notifyAddress,  conf.fromAddress, "");
				print "monitorSystems Turning FAN ON" 

		else:
			# no point if solar voltage on Pi power supply is below 4V

			print "solar voltage <= 4.0"
				

	if (hardwareactions.returnFanState()== False):
		print "monitorSystems FAN OFF:  No change in Fan State" 

	
	
	else:   
		# fan is on, look at turning off

	
		print "looking at turning fan off"
		# Fan control code - see about turning fan off

		#if temp inside is cooler than outside, turn fan off
		if ((insidetemperature < conf.FAN_OFF_TEMPERATURE) and (insidehumidity < conf.FAN_OFF_HUMIDITY)):
			hardwareactions.setfan(False)	
			pclogging.log(pclogging.INFO, __name__, "fanOFF insidehumid< FAN_ON_TEMPERATURE and insidehum < FAN_OFF_HUMIDITY")
			message = "Fan turning OFF:  State: ot:%3.2f it:%3.2f oh:%3.2f ih:%3.2f sv:%3.2f" % (outsidetemperature, insidetemperature, outsidehumidity, insidehumidity, solarvoltage)
			util.sendEmail("test", message,"ProjectCuracao Fan OFF(TH)", conf.notifyAddress,  conf.fromAddress, "");
			print "monitorSystems Turning FAN OFF" 


		if (solarvoltage <= 4.0):
			hardwareactions.setfan(False)
			pclogging.log(pclogging.INFO, __name__, "fanOFF solarvoltage =< 4.0 ")
			message = "Fan turning OFF SVcollapse:  State: ot:%3.2f it:%3.2f oh:%3.2f ih:%3.2f sv:%3.2f" % (outsidetemperature, insidetemperature, outsidehumidity, insidehumidity, solarvoltage)
			util.sendEmail("test", message, "ProjectCuracao Fan OFF(SV)", conf.notifyAddress,  conf.fromAddress, "");
			print "monitorSystems Turning FAN OFF" 
	

		if (hardwareactions.returnFanState()== True):
			print "monitorSystems FAN ON:  No change in Fan State" 

	
	# see about sending 5 minute alarms



		
