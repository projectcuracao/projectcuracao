
"""
testSetThresholds
JCS 11/7/2013 Version 1.0

"""

 
from datetime import datetime, timedelta
import sys
import time




sys.path.append('./datacollect')
sys.path.append('./graphprep')
sys.path.append('./hardware')
sys.path.append('./housekeeping')

import setThresholds



setThresholds.setThresholds("test",1)

