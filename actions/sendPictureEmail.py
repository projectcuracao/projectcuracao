
"""
 send Picture via Email
JCS 11/11/2013 Version 1.0

This program sends the last picture to email recipient
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

import util 
import hardwareactions

#if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf

def sendPictureEmail(source,delay):

	print("sendPictureEmail source:%s" % source)
	time.sleep(delay)


	

	util.sendEmail("test", "picture from ProjectCuracao", "Afternoon Picture", conf.notifyAddress, conf.fromAddress, "/home/pi/RasPiConnectServer/static/picamera.jpg");

