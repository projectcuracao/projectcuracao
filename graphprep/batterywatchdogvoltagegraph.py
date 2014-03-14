# batterywatchdog voltagepower graph generation 
# filename: batterywatchdogvoltagegraph.py
# Version 1.3 09/12/13
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

def  batterywatchdogvoltagegraph(source,days,delay):


	
	print("batterywatchdogvoltagegraph source:%s days:%s delay:%i" % (source,days,delay))
	print("sleeping :",delay)
	time.sleep(delay)
	print("batterywatchdogvoltagegraph running now")
	

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

		query = "SELECT TimeStamp, SolarOutputVoltage, BatteryOutputVoltage, ArInputVoltage FROM batterywatchdogdata where  now() - interval %i hour < TimeStamp" % (days*24)
		cursor.execute(query)
		result = cursor.fetchall()

		t = []
		s = []
		u = []
		v = []
		#x = []
		
		for record in result:
  			t.append(record[0])
  			s.append(record[1])
  			u.append(record[2])
  			v.append(record[3])
  			#x.append(record[4])
		print ("count of t=",len(t))
		#print (t)

		#dts = map(datetime.datetime.fromtimestamp, t)
		#print dts
		#fds = dates.date2num(t) # converted
		# matplotlib date format object
		hfmt = dates.DateFormatter('%m/%d-%H')

		fig = pyplot.figure()
		fig.set_facecolor('white')
		ax = fig.add_subplot(111,axisbg = 'white')
		#ax.vlines(fds, -200.0, 1000.0,colors='w')

		ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
		ax.xaxis.set_major_formatter(hfmt)
		ax.set_ylim(bottom = -200.0)
		pyplot.xticks(rotation='vertical')
		pyplot.subplots_adjust(bottom=.3)
		pylab.plot(t, s, color='b',label="Solar",linestyle="-",marker=".")
		pylab.plot(t, u, color='r',label="Battery",linestyle="-",marker=".")
		pylab.plot(t, v, color='g',label="Ar Input",linestyle="-",marker=".")
		pylab.xlabel("Hours")
		pylab.ylabel("Voltage")
		pylab.legend(loc='upper left')

		if (max(v) > max(s)):
			myMax = max(v)
		else:
			myMax = max(s)
		#pylab.axis([min(t), max(t), min(u), myMax])
	        pylab.axis([min(t), max(t), 0.0, 7.0])	
		pylab.figtext(.5, .05, ("Arduino System Power Last %i Days" % days),fontsize=18,ha='center')
		pyplot.setp( ax.xaxis.get_majorticklabels(), rotation=70)

		pylab.grid(True)

		pyplot.show()
		pyplot.savefig("/home/pi/RasPiConnectServer/static/batterywatchdogvoltage.png",facecolor=fig.get_facecolor())	

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
		del t, s, u, v
		gc.collect()
		print("batterywatchdogvoltagegraph finished now")
