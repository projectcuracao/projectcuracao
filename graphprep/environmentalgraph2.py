# environmental graph 2 
# filename:environmentalgraph2.py
# Version 1.0 10/13/13
#
# contains graphing code 
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

def  environmentalgraph2(source,days,delay):


	
	print("environmentalgraph2 source:%s days:%s" % (source,days))
	print("sleeping seconds:", delay)
	time.sleep(delay)
	print("envrironmentalgraph2 running now")
	

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

		query = "SELECT TimeStamp, BarometricPressure, Luminosity, FanState FROM environmentaldata where  now() - interval %i hour < TimeStamp" % (days*24)
		#query = "SELECT TimeStamp, InsideTemperature, InsideHumidity, OutsideTemperature, BarometricPressure, Luminosity, FanState  FROM environmentaldata where  now() - interval %i hour < TimeStamp" % (days*24)
		cursor.execute(query)
		result = cursor.fetchall()

		t = []
		s = []
		u = []
		v = []

		for record in result:
  			t.append(record[0])
  			s.append(record[1])
  			u.append(record[2])
  			v.append(record[3])

		#dts = map(datetime.datetime.fromtimestamp, s)
		#fds = dates.date2num(t) # converted
		# matplotlib date format object
		hfmt = dates.DateFormatter('%m/%d-%H')

		fig = pyplot.figure()
		
		ax = fig.add_subplot(111)
		
                #ax.vlines(fds, -200.0, 1000.0,colors='w')
                ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
		ax.xaxis.set_major_formatter(hfmt)
		pylab.xticks(rotation='vertical')

		pyplot.subplots_adjust(bottom=.3)
		pylab.plot(t, s, color='b',label="Barometric Pressure (mb) ",linestyle="-",marker=".")
		pylab.xlabel("Hours")
		pylab.ylabel("millibars")
		pylab.legend(loc='upper left')
		pylab.axis([min(t), max(t), 900, 1100])
		ax2 = pylab.twinx()
		pylab.ylabel("lux and  fan(0/1) ")

		# scale array

		for i in range(len(v)):
			v[i] = v[i] * 500
		

		pylab.plot(t, u, color='y',label="Luminosity (lux)",linestyle="-",marker=".")
		pylab.plot(t, v, color='r',label="Fan State (0/1)",linestyle="-",marker=".")
		pylab.axis([min(t), max(t), 0, max(u)])
		pylab.legend(loc='lower left')
		pylab.figtext(.5, .05, ("Environmental Statistics Last %i Days" % days),fontsize=18,ha='center')

		#pylab.grid(True)

		pyplot.setp( ax.xaxis.get_majorticklabels(), rotation=70)
		ax.xaxis.set_major_formatter(dates.DateFormatter('%m/%d-%H'))
		pyplot.show()
		pyplot.savefig("/home/pi/RasPiConnectServer/static/environmentalgraph2.png")	
		
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
		print("envrironmentalgraph2 finished now")

