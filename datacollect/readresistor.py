# read thermal resistor 
# filename: powerdatacollect.py
# Version 1.3 09/10/13
#
# contains event routines for data collection
#
#

import sys
import time
import math

from Adafruit_ADS1x15 import ADS1x15

import MySQLdb as mdb

def  getthermistortemperature(source, inputnumber):

	print("readresistor source:%s" % source)

	# now read temp

        ADS1015 = 0x00  # 12-bit ADC
        ADS1115 = 0x01  # 16-bit ADC

        # Initialise the ADC using the default mode (use default I2C address)
        # Set this to ADS1015 or ADS1115 depending on the ADC you are using!
        adc = ADS1x15(ic=ADS1015)

        # read channel 0 in single-ended mode, +/-4.096V, 250sps


	#/ resistance at 25 degrees C
	THERMISTORNOMINAL = 10000      
	#/ temp. for nominal resistance (almost always 25 C)
	TEMPERATURENOMINAL = 25   
	#/ how many samples to take and average, more takes longer
	#/ but is more 'smooth'
	NUMSAMPLES = 5
	#/ The beta coefficient of the thermistor (usually 3000-4000)
	BCOEFFICIENT  = 3950
	#/ the value of the 'other' resistor
	SERIESRESISTOR = 10000    
 
	samples = []
 
 
  	# take N samples in a row, with a slight delay
  	for i in range(NUMSAMPLES): 
		samples.append(adc.readADCSingleEnded(inputnumber, 4096, 250))
   		time.sleep(0.100)
 
	# average all the samples out
  	average = 0;
  	for i in range(NUMSAMPLES): 
     		average = average + samples[i]
  
	average = average/NUMSAMPLES
 
  	print("Average analog reading: %3.3f "% average) 
  
	# convert the value to resistance
  	average = (4096 / average) - 1
  	average = SERIESRESISTOR / average
 
  	print("Thermistor resistance: %5.3f " % average)
 


	steinhart = 0.0
  	steinhart = average / THERMISTORNOMINAL     #/ (R/Ro)
  	steinhart = math.log(steinhart)                  #/ ln(R/Ro)
  	steinhart = steinhart/BCOEFFICIENT                   #/ 1/B * ln(R/Ro)
  	steinhart = steinhart + 1.0 / (TEMPERATURENOMINAL + 273.15) #/ + (1/To)
  	steinhart = 1.0 / steinhart;                 #/ Invert
  	steinhart = steinhart - 273.15;                         #/ convert to C

	steinhart = steinhart - 7.59 # compared to thermometer 
  	print("Temperature: %2.4f *C " % steinhart)
	temperature = steinhart 
	
	return temperature
