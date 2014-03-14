"""
testUseCamera
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

import useCamera 
import hardwareactions



useCamera.takeSinglePicture("test", 1)
#time.sleep(5)
#useCamera.sweepShutter("test", 1)

