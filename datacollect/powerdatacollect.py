# power data collection events
# filename: powerdatacollect.py
# Version 1.3 09/10/13
#
# contains event routines for data collection
#
#

import sys
import time
import RPi.GPIO as GPIO

from Subfact_ina219 import INA219
from Adafruit_ADS1x15 import ADS1x15

import MySQLdb as mdb
import readresistor

sys.path.append('/home/pi/ProjectCuracao/main/config')

# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf

def  datacollect5minutes(source, delay):

	print("datacollect5minutes source:%s" % source)

	time.sleep(delay)
	# blink GPIO LED when it's run
        GPIO.setmode(GPIO.BOARD)
	GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)

	# now read in all the required data

        ina40 = INA219(0x40)
        ina41 = INA219(0x41)
        ina44 = INA219(0x44)
        current40 = ina40.getCurrent_mA() # pi
        current41 = ina41.getCurrent_mA() # battery
        current44 = ina44.getCurrent_mA() # solar

	if (current44 < 0):
		current44 = 0

        voltage40 = ina40.getBusVoltage_V()
        voltage41 = ina41.getBusVoltage_V()
        voltage44 = ina44.getBusVoltage_V()
	
	print("current40 = %3.2f" % current40) 
	print("current41 = %3.2f" % current41) 
	print("current44 = %3.2f" % current44) 
	
	print("voltage40 = %3.2f" % voltage40) 
	print("voltage41 = %3.2f" % voltage41) 
	print("voltage44 = %3.2f" % voltage44) 

	batterytemperature = readresistor.getthermistortemperature(source, 0)

	# power efficiency

        powerEfficiency = (current40*voltage40/(current41*voltage41+current44*voltage44))*100

	# if power Efficiency < 0, then must be plugged in so add 500ma @ 5V
	if (powerEfficiency < 0.0):
        	powerEfficiency = (current40*voltage40/(current41*voltage41+current44*voltage44+5.0*500.0))*100
		

	# now we have the data, stuff it in the database

	try:
		print("trying database")
    		con = mdb.connect('localhost', 'root', conf.databasePassword, 'ProjectCuracao');

    		cur = con.cursor()
		print "before query"

		query = 'INSERT INTO powersubsystemdata(TimeStamp, PiInputCurrent, PiInputVoltage, BatteryOutputCurrent, BatteryOutputVoltage, SolarOutputCurrent, SolarOutputVoltage, BatteryTemperature, PowerEfficiency) VALUES(UTC_TIMESTAMP(), %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f,%.3f)' % (current40, voltage40, current41, voltage41, current44, voltage44, batterytemperature, powerEfficiency) 
		print("query=%s" % query)

		cur.execute(query)
	
		con.commit()
		#cur.execute ("SELECT * FROM powersubsystemdata");

		# get the number of rows in the resultset
		
		#numrows = int(cur.rowcount)
		#print "numrows=", numrows

		#for x in range(0,numrows):
    		#	row = cur.fetchone()
    		#	print row[0], "-->", row[1]
		
	except mdb.Error, e:
  
    		print "Error %d: %s" % (e.args[0],e.args[1])
    		con.rollback()
    		#sys.exit(1)
    
	finally:    
       		cur.close() 
        	con.close()

		del cur
		del con

