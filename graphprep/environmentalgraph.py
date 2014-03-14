# environmental graph 
# filename:environmentalgraph.py
# Version 1.0 10/13/13
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

def  environmentalgraph(source,days,delay):


	
	print("environmentalgraph source:%s days:%s" % (source,days))
	print("sleeping seconds:", delay)
	time.sleep(delay)
	print("envrironmentalgraph running now")
	

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

		query = "SELECT TimeStamp, InsideTemperature, InsideHumidity, OutsideTemperature, OutsideHumidity FROM environmentaldata where  now() - interval %i hour < TimeStamp" % (days*24)
		#query = "SELECT TimeStamp, InsideTemperature, InsideHumidity, OutsideTemperature, BarometricPressure, Luminosity, FanState  FROM environmentaldata where  now() - interval %i hour < TimeStamp" % (days*24)
		cursor.execute(query)
		result = cursor.fetchall()

		t = []
		s = []
		u = []
		v = []
	        x = []	

		for record in result:
  			t.append(record[0])
  			s.append(record[1])
  			u.append(record[2])
  			v.append(record[3])
  			x.append(record[4])

		#dts = map(datetime.datetime.fromtimestamp, s)
		#fds = dates.date2num(dts) # converted
		# matplotlib date format object
		hfmt = dates.DateFormatter('%m/%d-%H')

		fig = pyplot.figure()
		
		ax = fig.add_subplot(111)
		ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
		ax.xaxis.set_major_formatter(hfmt)
		pylab.xticks(rotation='vertical')

		pyplot.subplots_adjust(bottom=.3)
		pylab.plot(t, s, color='b',label="Inside Temp (C) ",linestyle="-",marker=".")
		pylab.plot(t, v, color='g',label="Outside Temp (C)",linestyle="-",marker=".")
		pylab.xlabel("Hours")
		pylab.ylabel("degrees C")
		pylab.legend(loc='upper left')
		pylab.axis([min(t), max(t), 0, 50])
		ax2 = pylab.twinx()
		pylab.ylabel("% ")
		pylab.plot(t, x, color='y',label="Outside Hum %",linestyle="-",marker=".")
		pylab.plot(t, u, color='r',label="Inside Hum %",linestyle="-",marker=".")
		pylab.axis([min(t), max(t), 0, 100])
		pylab.legend(loc='lower left')
		pylab.figtext(.5, .05, ("Environmental Statistics Last %i Days" % days),fontsize=18,ha='center')

		#pylab.grid(True)

		pyplot.setp( ax.xaxis.get_majorticklabels(), rotation=70)
		ax.xaxis.set_major_formatter(dates.DateFormatter('%m/%d-%H'))
		pyplot.show()
		pyplot.savefig("/home/pi/RasPiConnectServer/static/environmentalgraph.png")	
		
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
		del t, s, u, v, x 
		gc.collect()
		print("envrironmentalgraph finished now")

