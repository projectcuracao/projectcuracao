#!/usr/bin/python

import time
import smbus
from Adafruit_I2C import Adafruit_I2C

# ===========================================================================
# BM017 / TCS34725 color sensor i2c driver Class
# From Adafruit and solutions-cubed C drivers
# John Shovic / Project Curacao
# Version 1.0
# 2/14/14
# projectcuracaopi@gmail.com
#
# ===========================================================================



class BM017:

	i2c = None

	# i2C Addresses

	__BM017_SensorAddress = 	0x29 
	__BM017_EnableAddress = 	0xa0 # register address + command bits
	__BM017_ATimeAddress = 		0xa1 # register address + command bits
	__BM017_ControlAddress = 	0xaf # register address + command bits
	__BM017_IDAddress = 		0xb2 # register address + command bits
	__BM017_ColorAddress = 		0xb4 # register address + command bits
	__BM017_StatusAddress =		0xb3 # register address + command bits
	__BM017_ClearInterrupts = 	0x66


	# bit definitions
	TCS34725_ENABLE_AIEN       = (0x10)    # RGBC Interrupt Enable
	TCS34725_ENABLE_WEN        = (0x08)    # Wait enable - Writing 1 activates the wait timer
	TCS34725_ENABLE_AEN        = (0x02)    # RGBC Enable - Writing 1 actives the ADC, 0 disables it
	TCS34725_ENABLE_PON        = (0x01)    # Power on - Writing 1 activates the internal oscillator, 0 disables it 

        # color results
	clear_color 	= 0
	red_color 	= 0
	green_color 	= 0
	blue_color 	= 0


	__BM017_IntegrationTime = 0xF6
	__BM017_Gain = 0x00

	debug = False


	def __init__(self, debug=False):
		self.i2c = Adafruit_I2C(self.__BM017_SensorAddress)

		self.i2c.write8(self.__BM017_ATimeAddress, self.__BM017_IntegrationTime)
		self.i2c.write8(self.__BM017_ControlAddress, self.__BM017_Gain)
		self.i2c.write8(self.__BM017_EnableAddress, 0x03)
		time.sleep(0.700)
		self.debug = debug

		if (self.debug):
			print("BM017 initialized")


	def isBM017There (self):

		device = self.i2c.readU8(self.__BM017_IDAddress)

		if (device == 0x44):
			if (self.debug):
				print ("BM017 / TCS34725 is present")
			return 1
		else:
			if (self.debug):
				print ("BM017 / TCS34725 is NOT present")
			return 0


	def readStatus (self):
		
		status = self.i2c.readU8(self.__BM017_StatusAddress)

		if (self.debug):
			print("BM017 Status=", status)

		return status


	def getColors(self):

		colorList = self.i2c.readList(self.__BM017_ColorAddress, 8)

		if (self.debug):
			print("ColorList = ", colorList)

		self.clear_color = (colorList[1] << 8) + (colorList[0])
		self.red_color = (colorList[3] << 8) + (colorList[2])
		self.green_color = (colorList[5] << 8) + (colorList[4])
		self.blue_color = (colorList[7] << 8) + (colorList[6])

		if (self.debug):
			print("clear_color= ", self.clear_color)
			print("red_color= ", self.red_color)
			print("green_color= ", self.green_color)
			print("blue_color= ", self.blue_color)


	def setIntegrationTimeAndGain(self, IT, Gain):

		self.i2c.write8(self.__BM017_ATimeAddress, IT)
		self.i2c.write8(self.__BM017_ControlAddress, Gain)
		self.i2c.write8(self.__BM017_EnableAddress, 0x03)
		time.sleep(0.700)
	
		if (self.debug):
			print("IT set to:", IT)
			print("Gain set to:", Gain)
		__BM017_IntegrationTime = IT
		__BM017_Gain = Gain


	def disableDevice(self):

		reg = self.i2c.readU8(self.__BM017_EnableAddress)

		self.i2c.write8(self.__BM017_EnableAddress, reg & ~(self.TCS34725_ENABLE_PON | self.TCS34725_ENABLE_AEN));
		

	# This can be used to trigger the LED.  Connect the INT pin to LEDON pin and connecting the VDD_LED pin to 3.3V 
	def setInterrupt(self, state):

	  	reg = self.i2c.readU8(self.__BM017_EnableAddress)
	    	if (state):
	        	reg |= self.TCS34725_ENABLE_AIEN
			if(self.debug):
				print("Interrupt On")
		else: 
		      	reg &= ~self.TCS34725_ENABLE_AIEN
			if(self.debug):
				print("Interrupt Off")

		self.i2c.write8(self.__BM017_EnableAddress, reg)




	def clearInterrupt(self): 
		self.i2c.write8(0x66, 0x00)


 	def setInterruptLimits(self, low, high):

		self.i2c.write8(0x04, low & 0xFF)
		self.i2c.write8(0x05, low >> 8)
		self.i2c.write8(0x06, high & 0xFF)
		self.i2c.write8(0x07, low >> 8)
