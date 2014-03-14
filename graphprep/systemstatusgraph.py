# system status generation 
# filename:systemstatusgraph.py
# Version 1.0 10/07/13
#
# contains event routines for data collection
#
#

import sys
import time
import RPi.GPIO as GPIO

import gc
import datetime

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

from matplotlib import pyplot
from matplotlib import dates

import pylab

import MySQLdb as mdb

sys.path.append('/home/pi/ProjectCuracao/main/config')

# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf

def  systemstatusgraph(source,days,delay):


	
	print("systemstatusgraph source:%s days:%s delay:%i" % (source,days,delay))
	print("sleeping seconds:",delay)
	time.sleep(delay)
	print("systemstatusgraph running now")
	

	# blink GPIO LED when it's run
	GPIO.setmode(GPIO.BOARD)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)

	# now we have get the data, stuff it in the graph 

	try:
		print("trying database")
    		db = mdb.connect('localhost', 'root', conf.databasePassword, 'ProjectCuracao');

    		cursor = db.cursor()

		query = "SELECT TimeStamp, freememory, freediskspace, cputemp, ProjectProcessMemoryPercent, RasPiConnectProcessMemoryPercent  FROM systemstatistics where  now() - interval %i hour < TimeStamp" % (days*24)
		#query = "SELECT TimeStamp, SolarOutputCurrent, BatteryOutputCurrent, PiInputCurrent, PowerEfficiency FROM powersubsystemdata where  now() - interval %i hour < TimeStamp" % (days*24)
		cursor.execute(query)
		result = cursor.fetchall()

		t = []
		s = []
		u = []
		v = []
		x = []
		y = []
		
		for record in result:
  			t.append(record[0])
  			s.append(record[1])
  			u.append(record[2])
  			v.append(record[3])
  			x.append(record[4])
  			y.append(record[5])

		#dts = map(datetime.datetime.fromtimestamp, s)
		fds = dates.date2num(t) # converted
		# matplotlib date format object
		hfmt = dates.DateFormatter('%m/%d-%H')

		fig = pyplot.figure()
		ax = fig.add_subplot(111)
		ax.vlines(fds, -200.0, 1000.0,colors= 'w')

		ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
		ax.xaxis.set_major_formatter(hfmt)
		ax.set_ylim(bottom = -200.0)
		pyplot.xticks(rotation='vertical')
		pyplot.subplots_adjust(bottom=.3)
		pylab.plot(t, s, color='b',label="free memory %",linestyle="-",marker=".")
		pylab.plot(t, u, color='r',label="free disk %",linestyle="-",marker=".")
		pylab.plot(t, v, color='g',label="cputemp (C)",linestyle="-",marker=".")
		pylab.plot(t, x, color='m',label="Project Mem %",linestyle="-",marker=".")
		pylab.plot(t, y, color='c',label="Server Mem %",linestyle="-",marker=".")
		pylab.xlabel("Hours")
		pylab.ylabel("% or degrees C")
		pylab.legend(loc='upper left')

		pylab.axis([min(t), max(t), 0, 100])
		#pylab.title(("System Power Last %i Days" % days),ha='right')
		pylab.figtext(.5, .05, ("System Statistics Last %i Days" % days),fontsize=18,ha='center')

		pylab.grid(True)

		pyplot.show()
		pyplot.savefig("/home/pi/RasPiConnectServer/static/systemstatistics.png")	
		
	except mdb.Error, e:
  
    		print "Error %d: %s" % (e.args[0],e.args[1])
    
	finally:    

		cursor.close()       	 
        	db.close()

		del cursor
		del db

		fig.clf()
		pyplot.close()
		pylab.close()
		del t, s, u, v, x, y
		gc.collect()
		print("systemstatusgraph finished now")

