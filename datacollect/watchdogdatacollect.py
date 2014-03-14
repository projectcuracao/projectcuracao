# Battery Watchdog Data collection events
# filename: watchdogdatacollect.py
# Version 1.5 01/10/14
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
sys.path.append('./housekeeping')
import pclogging
import util
import sendWatchDogTimer

sys.path.append('/home/pi/ProjectCuracao/main/config')

# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf



def  watchdogdatacollect(source, delay):

	print("watchdogdatacollect source:%s" % source)

	time.sleep(delay)
	# blink GPIO LED when it's run
	GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)
        time.sleep(0.5)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)
        time.sleep(0.5)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)



	# setup serial port to Arduino

	# interrupt Arduino to start listening

	GPIO.setmode(GPIO.BOARD)
    	GPIO.setup(7, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)	
	GPIO.output(7, False)
	GPIO.output(7, True)
	GPIO.output(7, False)
	

	ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
	#ser.open()
	#time.sleep(7.0)
	time.sleep(9.0)


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
	# send the watchdog timer first
	sendWatchDogTimer.sendWatchDogTimer("watchdogdatacollect", 0,ser)


	
	# Send the GD (Get Data) Command
        response = util.sendCommandAndRecieve(ser, "GD")
	print("response=", response);
	


	# stuff the values into variables
	splitList = response.split(',')
	print(splitList)	

	for item in range(len(splitList)):
		splitList[item] = splitList[item].replace('NAN', "0.0")
	print(splitList)	

	if (len(splitList) == 15):
		ArInputVoltage = float(splitList[0])
        	ArInputCurrent = float(splitList[1])
		SolarCellVoltage = float(splitList[2])
		SolarCellCurrent = float(splitList[3])
		BatteryVoltage = float(splitList[4])
		BatteryCurrent = float(splitList[5])
		OutsideHumidity = float(splitList[6])
		OutsideTemperature = float(splitList[7])
		LastReboot = splitList[8]
		BatteryTemperature = float(splitList[9])
		FreeMemory = float(splitList[10])
		UnregulatedWindVoltage = float(splitList[11])
		RegulatedWindVoltage = float(splitList[12])
		SolarWind = int(splitList[13])
		ArduinoPiBatteryVoltage = float(splitList[14])
	else:
		print "bad response from GD"
		# system setup

		pclogging.log(pclogging.ERROR, __name__, "GD failed from Pi to BatteryWatchDog")

		# say goodby  
        	response = util.sendCommandAndRecieve(ser, "GB")
		print("response=", response);
		ser.close()
		return
	
	print("ArInputCurrent =", ArInputCurrent)

     	# power efficiency
	if ( (SolarCellCurrent*SolarCellVoltage+BatteryCurrent*BatteryVoltage) == 0):
       		powerEfficiency = 10000.0; 
	else:
		powerEfficiency = (ArInputCurrent*ArInputVoltage/(SolarCellCurrent*SolarCellVoltage+BatteryCurrent*BatteryVoltage))*100


        # if power Efficiency < 0, then must be plugged in so add 500ma @ 5V
        if (powerEfficiency < 0.0):
		if ((SolarCellCurrent*SolarCellVoltage+BatteryCurrent*BatteryVoltage+5.0*500.0) == 0.0):
			powerEfficiency = 10000.0;
		else:	
        		powerEfficiency = (ArInputCurrent*ArInputVoltage/(SolarCellCurrent*SolarCellVoltage+BatteryCurrent*BatteryVoltage+5.0*500.0))*100


	# get the unread log from the Arduino
        response = util.sendCommandAndRecieve(ser, "SL")
	print("response=", response)
	
	try:
		countEntry  = int(response)
	except ValueError:
	    	countEntry = 0


	if (countEntry > 0):
		# read all unread entries
		for i in range(countEntry):
			logEntry = util.recieveLine(ser)
			print("recievedLogEntry =", logEntry)
			# parse and then stuff in log database
			# stuff the values into variables
			splitList = logEntry.split(',')
			print(splitList)	

			if (len(splitList) == 4):
				ArduinoTime = splitList[0]
				ArduinoLevel = int(splitList[1])
				ArduinoData0 = int(splitList[2])
				ArduinoData1 = splitList[3]
				# now we have the data, stuff it in the database
				entryValue = util.convertArduinoEntry01ToText(ArduinoData0, ArduinoData1)
			
				if (ArduinoData0 == 9):
					# LOGAlarmTriggered
					entryValue = util.convertAlarmToText(int(ArduinoData1))

				try:
					print("trying database")
    					con = mdb.connect('localhost', 'root', conf.databasePassword, 'ProjectCuracao');
	
    					cur = con.cursor()
					print "before query"
	
                			query = "INSERT INTO systemlog(TimeStamp, Level, Source, Message) VALUES('%s', '%s', '%s', '%s')" % (ArduinoTime, ArduinoLevel,  'Ardinuo BatteryWatchDog', entryValue)
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

			else:
				print "bad response from SL"
				# system setup
	
				pclogging.log(pclogging.ERROR, __name__, "SL failed from Pi to BatteryWatchDog")
	
				# say goodby  
        			response = util.sendCommandAndRecieve(ser, "GB")
				print("response=", response);
				ser.close()
				return
	
	print("ArInputCurrent =", ArInputCurrent)


	# say goodby  
        response = util.sendCommandAndRecieve(ser, "GB")
	print("response=", response);

	ser.close()
		
	# now we have the data, stuff it in the database

	try:
		print("trying database")
    		con = mdb.connect('localhost', 'root', conf.databasePassword, 'ProjectCuracao');

    		cur = con.cursor()
		print "before query"

		query = 'INSERT INTO batterywatchdogdata(TimeStamp, ArInputCurrent, ArInputVoltage, BatteryOutputCurrent, BatteryOutputVoltage, SolarOutputCurrent, SolarOutputVoltage, BatteryTemperature, PowerEfficiency, LastReboot, OutsideTemperature, OutsideHumidity, FreeMemory, UnregulatedWindVoltage, RegulatedWindVoltage, SolarWind,ArduinoPiBatteryVoltage) VALUES(UTC_TIMESTAMP(), %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f,%.3f,%s, %.3f, %.3f, %i, %.3f, %.3f, %i, %.3f)' % (ArInputCurrent, ArInputVoltage, BatteryCurrent, BatteryVoltage, SolarCellCurrent, SolarCellVoltage, BatteryTemperature, powerEfficiency, LastReboot, OutsideTemperature, OutsideHumidity, FreeMemory, UnregulatedWindVoltage, RegulatedWindVoltage, SolarWind, ArduinoPiBatteryVoltage)
		print("query=%s" % query)

		cur.execute(query)
	
		con.commit()
		# pclogging.log(pclogging.INFO, __name__, "RD OK from Pi to BatteryWatchDog")
		
	except mdb.Error, e:
  
    		print "Error %d: %s" % (e.args[0],e.args[1])
    		con.rollback()
    		#sys.exit(1)
    
	finally:    
       		cur.close() 
        	con.close()

		del cur
		del con
