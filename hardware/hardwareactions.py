#!/usr/bin/python
# hardwareactions.py
# routines for setting hardware for ProjectCuracao
# jcs 10/31/13
#
import sys
import time
import RPi.GPIO as GPIO
#from RPIO import PWM
#import RPIO 
from Adafruit_ADS1x15 import ADS1x15

def setfan(value):

	#return TRUE if successful (can't tell with Fan - I suppose we could by looking at current)
	
	GPIO.setmode(GPIO.BOARD)

	if (value == True):
 	      GPIO.setup(18, GPIO.OUT)
              GPIO.output(18, True)
	      time.sleep(0.1)
              GPIO.output(18, False)
              f = open("/home/pi/ProjectCuracao/main/state/fanstate.txt", "w")
              f.write("1")
              f.close()
              return True

        if (value == False):
 	      GPIO.setup(15, GPIO.OUT)
              GPIO.output(15, True)
	      time.sleep(0.1)
              GPIO.output(15, False)
              f = open("/home/pi/ProjectCuracao/main/state/fanstate.txt", "w")
              f.write("0")
              f.close()
              return True

        return True

def returnFanState():


	# Fan State
	
	# read from fan state file
        try:
		f = open("./state/fanstate.txt", "r")
		tempString = f.read()
        	f.close()
        	fanstate = int(tempString)
	except IOError as e:
		fanstate = 0

	return fanstate


def openshutter():

	LOWTHRESHOLD = 1100
	print "opening shutter"
	
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(12, GPIO.OUT)
	servo = GPIO.PWM(12, 50)
	servo.start(4.0) # 800us
	time.sleep(1.5)

	servo.stop()
	feedbackvalue = readCameraServo()
	print "openshutter feedbackvalue =", feedbackvalue

	if (feedbackvalue > LOWTHRESHOLD):
		# try again
		servo = GPIO.PWM(12, 50)
		servo.start(4) # 800us
		time.sleep(1.5)

		servo.stop()
		feedbackvalue = readCameraServo()
		print "openshutter-2 feedbackvalue =", feedbackvalue
		# now if failed, report it 
		if (feedbackvalue > LOWTHRESHOLD):
			#GPIO.cleanup()
			return False;

			

	#GPIO.cleanup()
	return True;


def closeshutter():

	HIGHTHRESHOLD = 1650 
	print "closing shutter"


	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(12, GPIO.OUT)
	servo = GPIO.PWM(12, 50)
	servo.start(8) # 1600us
	time.sleep(1.5)
	servo.stop()
	feedbackvalue = readCameraServo()
	print "closeshutter feedbackvalue =", feedbackvalue


	if (feedbackvalue < HIGHTHRESHOLD):
		servo = GPIO.PWM(12, 50)
		servo.start(8) # 1600us
		time.sleep(1.5)
		servo.stop()
		feedbackvalue = readCameraServo()
		print "closeshutter - 2 feedbackvalue =", feedbackvalue
		if (feedbackvalue < HIGHTHRESHOLD):
			#GPIO.cleanup()
			print "openshutter value=", readCameraServo()
			return False

	return True


def sweepshutter():

	print "sweeping shutter"

	# close it
	closeshutter();

	openshutter();

	print "in middle"
	
	closeshutter();

	return True;




def  readCameraServo():



        ADS1015 = 0x00  # 12-bit ADC
        ADS1115 = 0x01  # 16-bit ADC

        # Initialise the ADC using the default mode (use default I2C address)
        # Set this to ADS1015 or ADS1115 depending on the ADC you are using!
        adc = ADS1x15(ic=ADS1015)
	value = adc.readADCSingleEnded(1, 4096, 250)
	
	return value
