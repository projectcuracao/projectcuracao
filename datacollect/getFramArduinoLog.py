
# Get FRAMArduino Log 
# filename: getArduinoLog.py
# Version 1.4 10/10/14
#
# get FRAM logs from Arduino 
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

sys.path.append('/home/pi/ProjectCuracao/main/config')

# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf



def  getFramArduinoLog(source, delay):

	print("Fram Log datacollect source:%s" % source)

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
	ser.flushInput()
	ser.flushOutput()
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


	# get the unread log from the Arduino
        response = util.sendCommandAndRecieve(ser, "SLF")
	print("response=", response)
	
	try:
		countEntry  = int(response)
	except ValueError:
	    	countEntry = 0

	print("countEntry=", countEntry)
	
	if (countEntry > 0):
		# read all unread entries
		for i in range(countEntry):
			logEntry = util.recieveLine(ser)
			print("recievedLogEntry =", logEntry)
			# parse and then stuff in log database
			# stuff the values into variables
			splitList = logEntry.split(',')
			print(splitList)	

			if (len(splitList) == 11):
				WeatherLogTime = splitList[0]
				WeatherLogCWS = float(splitList[1])
				WeatherLogCWG = float(splitList[2])
				WeatherLogCWD = float(splitList[3])
				WeatherLogCWDV = float(splitList[4])
				WeatherLogCR = float(splitList[5])
				WeatherLogURWV = float(splitList[6])
				WeatherLogRWV = float(splitList[7])
				WeatherLogPIS = float(splitList[8])
				WeatherLogWSCUR = float(splitList[9])
				WeatherLogSolarOrWind = int(splitList[10])
				# now we have the data, stuff it in the database
			
				try:
					print("trying database")
    					con = mdb.connect('localhost', 'root', conf.databasePassword, 'ProjectCuracao');
	
    					cur = con.cursor()
					print "before query"
	
                			query = "INSERT INTO weatherdata(TimeStamp, CWS, CWG, CWD, CWDV, CR, URWV, RWV, PIS,WSCUR, SolarOrWind) VALUES('%s', '%s', '%s', '%s', '%s',  '%s', '%s', '%s', '%s', '%s', %i)" % (WeatherLogTime, WeatherLogCWS,  WeatherLogCWG, WeatherLogCWD, WeatherLogCWDV, WeatherLogCR,WeatherLogURWV, WeatherLogRWV, WeatherLogPIS, WeatherLogWSCUR,  WeatherLogSolarOrWind)
					


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
				print "bad response from SLF"
				# system setup
	
				pclogging.log(pclogging.ERROR, __name__, "SLF failed from Pi to BatteryWatchDog")
	
				# say goodby  
        			response = util.sendCommandAndRecieve(ser, "GB")
				print("response=", response);
				ser.close()
				return
	

	# say goodby  
        response = util.sendCommandAndRecieve(ser, "GB")
	print("response=", response);

	ser.close()
