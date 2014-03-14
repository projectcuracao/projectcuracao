#
#
# general utilities
# JCS 10/30/13
#
#
import time
import sys
import os
import httplib
import json

sys.path.append('/home/pi/ProjectCuracao/main/config')
sys.path.append('/home/pi/ProjectCuracao/main/hardware')
sys.path.append('/home/pi/ProjectCuracao/main/util')
sys.path.append('/home/pi/ProjectCuracao/main/pclogging')
import util
import hardwareactions
import pclogging

def convertAlarmToText(alarm):

	alarmName = str(alarm)
	if (alarm == 0):
		alarmName = "AlarmPiShutdown"
	if (alarm == 1):
		alarmName = "AlarmPiStartup"
	if (alarm == 2):
		alarmName = "AlarmPiMidnightStartup"
	if (alarm == 3):
		alarmName = "AlarmPiMidnightShutdown"
	if (alarm == 4):
		alarmName = "AlarmPiVoltageShutdown"
	if (alarm == 5):
		alarmName = "AlarmPiSunset"
	if (alarm == 6):
		alarmName = "AlarmPiSunrise"
	return alarmName


def convertLogLevelToText(level):

	levelName = str(level)	
	if (level == pclogging.DEBUG):
		levelName = "DEBUG"
	if (level == pclogging.INFO):
		levelName = "INFO"
	if (level == pclogging.WARNING):
		levelName = "WARNING"
	if (level == pclogging.ERROR):
		levelName = "ERROR"
	if (level == pclogging.CRITICAL):
		levelName = "CRITICAL"

	return levelName

def convertArduinoEntry01ToText(entry0,entry1):

	entryName = "UNKNOWN %i %s " % (entry0, entry1)
	if (entry0 == 0):
		entryName ="LOGNoEvent"
	if (entry0 == 1):
		entryName ="LOGPiShutdown"
	if (entry0 == 2):
		entryName ="LOGPiStartup"
	if (entry0 == 3):
		entryName ="LOGPiOff"
	if (entry0 == 4):
		entryName ="LOGPiOn"
	if (entry0 == 5):
		# LOGPiPower has voltage as entryData1
		entryName ="LOGPiPower: %s" % entry1
	if (entry0 == 6):
		# LOGPiInterrupt has reason as entryData1
		if (entry1 == "0"):
			myentry1 = "NOINTERRUPT" 
		if (entry1 == "1"):
			myentry1 = "NOREASON" 
		if (entry1 == "2"):
			myentry1 = "SHUTDOWN"
		if (entry1 == "3"):
			myentry1 = "GETLOG" 
		if (entry1 == "4"):
			myentry1 = "ALARM1" 
		if (entry1 == "5"):
			myentry1 = "ALARM2" 
		if (entry1 == "6"):
			myentry1 = "ALARM3" 
		if (entry1 == "7"):
			myentry1 = "REBOOT"
		entryName ="LOGPiInterrupt: %s" % myentry1
	if (entry0 == 7):
		entryName ="LOGThresholdsSet"
	if (entry0 == 8):
		# LOGSensorFail has sensor # (i2c address) as entryData1
		entryName ="LOGSensorFail: %s" % entry1
	if (entry0 == 9):
		# LOGAlarmTriggered has alarm # (as in the check alarm routine) as entryData1
		entryAlarm = util.convertAlarmToText(entry1)

		entryName ="LOGAlarmTriggered: %s" % entryAlarm
	if (entry0 == 10):
		entryName ="LOGDeadManSwitchTriggered"
	if (entry0 == 11):
		entryName ="LOGArduinoReboot"
	if (entry0 == 12):
		entryName ="LOGWatchDogTriggered"
	if (entry0 == 13):
		# LOGAlarmTriggered has alarm # (as in the check alarm routine) as entryData1
		entryName ="LOGAlarmDisabled: %s" % entry1
	if (entry0 == 14):
		entryName ="LOGPiOnOverruledUnderVoltage"
	if (entry0 == 15):
		entryName ="LOGPiOffLowVoltage"
	if (entry0 == 16):
		entryName ="LOGPiOnLowVoltageRecovery"
	if (entry0 == 17):
		entryName ="LOGSolarSelect"
	if (entry0 == 18):
		entryName ="LOGWindSelect"
	if (entry0 == 19):
		entryName ="LOGVoltageCancelledRecovery"
	if (entry0 == 20):
		entryName ="LOGBad5RTCRead"
	return entryName	



def  sendCommandAndRecieve(ser,command):

     timeout = True
     # send the first "are you there? command - RD - return from Arduino OK"
     print("sending command=",command)
     ser.write(command+'\n') 
     # wait no more than 10 seconds
     t = 10
                
     st = ''
     initTime = time.time()
     while True:
               st +=  ser.readline()
	       print("right after readline.  st=",st)
	       if (len(st) > 0):
			break;
	       print("after readline.  st=",st)
               if timeout and (time.time() - initTime > t) :
                    break


     return st	

def  recieveLine(ser):

     timeout = True
     t = 10
                
     st = ''
     initTime = time.time()
     while True:
               st +=  ser.readline()
	       if (len(st) > 0):
			break;
	       print("after readline.  st=",st)
               if timeout and (time.time() - initTime > t) :
                    break


     return st	


def returnPercentLeftInBattery(currentVoltage, maxVolt):

	scaledVolts = currentVoltage / maxVolt
	
	if (scaledVolts > 1.0):
		scaledVolts = 1.0
	
	
	if (scaledVolts > .9686):
		returnPercent = 10*(1-(1.0-scaledVolts)/(1.0-.9686))+90
		return returnPercent

	if (scaledVolts > 0.9374):
		returnPercent = 10*(1-(0.9686-scaledVolts)/(0.9686-0.9374))+80
		return returnPercent


	if (scaledVolts > 0.9063):
		returnPercent = 30*(1-(0.9374-scaledVolts)/(0.9374-0.9063))+50
		return returnPercent

	if (scaledVolts > 0.8749):
		returnPercent = 30*(1-(0.8749-scaledVolts)/(0.9063-0.8749))+20
		return returnPercent

	
	if (scaledVolts > 0.8437):
		returnPercent = 17*(1-(0.8437-scaledVolts)/(0.8749-0.8437))+3
		return returnPercent


   	if (scaledVolts > 0.8126):
		returnPercent = 1*(1-(0.8126-scaledVolts)/(0.8437-0.8126))+2
		return returnPercent



	if (scaledVolts > 0.7812):
		returnPercent = 1*(1-(0.7812-scaledVolts)/(0.7812-0.8126))+1
		return returnPercent

	return 0	




def sendEmail(source, message, subject, toaddress, fromaddress, filename):

	# if conflocal.py is not found, import default conf.py

	# Check for user imports
	try:
     		import conflocal as conf
	except ImportError:
     		import conf

	# Import smtplib for the actual sending function
	import smtplib

	# Here are the email package modules we'll need
	from email.mime.image import MIMEImage
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText

	COMMASPACE = ', '

	# Create the container (outer) email message.
	msg = MIMEMultipart()
	msg['Subject'] = subject 
	# me == the sender's email address
	# family = the list of all recipients' email addresses
	msg['From'] = fromaddress
	msg['To'] =  toaddress
	#msg.attach(message) 

	mainbody = MIMEText(message, 'plain')
	msg.attach(mainbody)

	# Assume we know that the image files are all in PNG format
    	# Open the files in binary mode.  Let the MIMEImage class automatically
       	# guess the specific image type.
	if (filename != ""):
    		fp = open(filename, 'rb')
       		img = MIMEImage(fp.read())
    		fp.close()
        	msg.attach(img)

	# Send the email via our own SMTP server.

	try:
		# open up a line with the server
		s = smtplib.SMTP("smtp.gmail.com", 587)
		s.ehlo()
		s.starttls()
		s.ehlo()

		# login, send email, logout
		s.login(conf.mailUser, conf.mailPassword)
		s.sendmail(conf.mailUser, toaddress, msg.as_string())
		#s.close()


		s.quit()

	except:
		
		print("sendmail exception raised")
	return 0



def rebootPi(why):
   sendEmail("test", "ProjectCuracao Pi reboot\n" + why, "The Raspberry Pi is rebooting.", conf.notifyAddress,  conf.fromAddress, "");
   # shut the shutter on camera
   hardwareactions.closeshutter();
   sys.stdout.flush()
   os.system("sudo reboot")

def shutdownPi(why):

   sendEmail("test", "ProjectCuracao Pi shutdown\n" + why, "The Raspberry Pi is shutting down.", conf.notifyAddress,  conf.fromAddress, "");
   # shut the shutter on camera
   hardwareactions.closeshutter();
   sys.stdout.flush()
   os.system("sudo shutdown -h now")


def track_ip():
   """
   Returns Dict with the following keys:
   - ip
   - latlong
   - country
   - city
   - user-agent
   """

   conn = httplib.HTTPConnection("www.trackip.net")
   conn.request("GET", "/ip?json")
   resp = conn.getresponse()
   print resp.status, resp.reason

   if resp.status == 200:
       ip = json.loads(resp.read())
   else:
       print 'Connection Error: %s' % resp.reason

   conn.close()
   return ip
