
"""
testEmail
JCS 10/31/2013 Version 1.0

This program runs the data collection from the watchdog
"""

# shelves:
# 	datacollect - sensor data collection - disabled to RAM
#	graphprep - building system graphs
#	housekeeping - fan check , general health and wellfare
# 	alarmchecks - checks for system health alarms 
#	actions - specific actions scheduled (i.e. camera picture)
 
from datetime import datetime, timedelta
import sys
import time



sys.path.append('./datacollect')
sys.path.append('./graphprep')
sys.path.append('./hardware')
sys.path.append('./housekeeping')
sys.path.append('./actions')
sys.path.append('./util')

import util 
import hardwareactions

#if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf

print("conf.notifyAddress", conf.notifyAddress)
print("conf.fromAddress", conf.fromAddress)

util.sendEmail("test", "hello from ProjectCuracao", "Test from Pi", conf.notifyAddress, conf.fromAddress, "/home/pi/RasPiConnectServer/static/picamera.jpg");

