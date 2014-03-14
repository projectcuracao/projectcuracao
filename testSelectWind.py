

"""
testSelectWind.py
JCS 01/14/2014 Version 1.0

This program selects Wind 
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

from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.shelve_store import ShelveJobStore



sys.path.append('./datacollect')
sys.path.append('./graphprep')
sys.path.append('./hardware')
sys.path.append('./housekeeping')
sys.path.append('./alarmchecks')
sys.path.append('./actions')
import selectWind 


print( "result=",selectWind.selectWind("test", 1) )

