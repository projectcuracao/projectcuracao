


"""
testFramRead.py
JCS 10/10/2014 Version 1.0

This program runs the data collection, graph preperation, housekeeping and actions
"""

 
from datetime import datetime, timedelta
import sys
import time


sys.path.append('./datacollect')
sys.path.append('./graphprep')
sys.path.append('./hardware')
sys.path.append('./housekeeping')

import getFramArduinoLog 


getFramArduinoLog.getFramArduinoLog("test",1)

