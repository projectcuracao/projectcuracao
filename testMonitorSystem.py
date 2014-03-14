"""
test monitorSystem
JCS 10/31/2013 Version 1.0

This program runs the data collection from the watchdog
"""

from datetime import datetime, timedelta
import sys
import time



sys.path.append('./datacollect')
sys.path.append('./graphprep')
sys.path.append('./hardware')
sys.path.append('./housekeeping')
sys.path.append('./actions')
sys.path.append('./util')

import monitorSystem 



while (True):
	monitorSystem.monitorSystem("test", 1)
	time.sleep(5.0)

