
"""
test DoAllGraphs 
JCS 1/27/2014 Version 1.0

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

import doallgraphs 



doallgraphs.doallgraphs("test", 10, 5)

