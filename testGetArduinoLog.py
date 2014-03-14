


"""
testGetArduinoLog.py
JCS 1/04/2014 Version 1.0

This program runs the data collection of logs from the watchdog
"""

 
from datetime import datetime, timedelta
import sys
import time




sys.path.append('./datacollect')
sys.path.append('./graphprep')
sys.path.append('./hardware')
sys.path.append('./housekeeping')

import getArduinoLog 


#while True:
getArduinoLog.getArduinoLog("test", 1)
#time.sleep(15.0)

