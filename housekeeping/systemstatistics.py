# collect raspberry pi system statistics
# filename: powerdatacollect.py
# Version 1.3 09/10/13
#
# contains event routines for data collection
#
#

import sys
import time
import RPi.GPIO as GPIO
import subprocess
import MySQLdb as mdb
import psutil

sys.path.append('/home/pi/ProjectCuracao/main/config')

# if conflocal.py is not found, import default conf.py

# Check for user imports
try:
	import conflocal as conf
except ImportError:
	import conf

def  systemstatistics15minutes(source,delay):

	print("systemstatistics15minutes source:%s" % source)
	time.sleep(delay)
	# blink GPIO LED when it's run
        GPIO.setmode(GPIO.BOARD)
	GPIO.setup(22, GPIO.OUT)
        GPIO.output(22, False)
        time.sleep(0.5)
        GPIO.output(22, True)

	# collect system stat
	#
	# timestamp
	# freememory
	# freeswapspace
	# freediskspace
	# cputemp
	# cpuload
	# processcount
	# lastboot
	# ProjectProcessMemoryPercent
	# RasPiConnectProcessMemoryPercent

	# memory
	vmemory = psutil.virtual_memory()
	print vmemory.percent
	smemory = psutil.swap_memory()
	print smemory.percent

	# disk
	dusage = psutil.disk_usage('/') 
	print dusage.percent	

	#last boot

	boottime = psutil.BOOT_TIME
	print boottime

	#cpu load
	
	cpuload = psutil.cpu_percent(interval=1.0)
	print cpuload

	#processes

	processcount = psutil.get_pid_list()

	process = filter(lambda p: p.name == "python", psutil.process_iter())

	ProjectCuracaoPercent = 0.0	
	RasPiConnectProcessMemoryPercent = 0.0	
	for i in process:

		if (len(i.cmdline) > 1):
			if (i.cmdline[1] == "ProjectCuracao.py" ):
  				print "ProjectCuracao=", i.name,i.pid, i.cmdline, i.get_memory_percent()
				# print i.get_memory_maps()
				ProjectCuracaoPercent = i.get_memory_percent()

			if (i.cmdline[1] == "RasPiConnectServer.py" ):
  				print "RasPiConnect=",i.name,i.pid, i.cmdline, i.get_memory_percent()
				# print i.get_memory_maps()
				RasPiConnectProcessMemoryPercent = i.get_memory_percent()




    	output = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
        cputemp = float(output)/1000.0

	# now we have the data, stuff it in the database

	try:
		print("trying database")
    		con = mdb.connect('localhost', 'root', conf.databasePassword, 'ProjectCuracao');

    		cur = con.cursor()
		print "before query"
	# timestamp
	# freememory
	# freeswapspace
	# freediskspace
	# cputemp
	# load
	# lastboot
	# ProjectProcessMemoryPercent
	# RasPiConnectProcessMemoryPercent

		query = 'INSERT INTO systemstatistics(TimeStamp, freememory, freeswapspace, freediskspace, cputemp, cpuload, processcount, lastboot, ProjectProcessMemoryPercent, RasPiConnectProcessMemoryPercent) VALUES(UTC_TIMESTAMP(), %.2f, %.2f, %.2f, %.2f, %.2f, %i, FROM_UNIXTIME(%i), %.2f, %.2f)' % (100.0 - vmemory.percent, 100.0 - smemory.percent, 100.0 - dusage.percent, cputemp, cpuload, len(processcount), boottime, ProjectCuracaoPercent, RasPiConnectProcessMemoryPercent) 
		print("query=%s" % query)

		cur.execute(query)
	
		con.commit()
		
		
	except mdb.Error, e:
  
    		print "Error %d: %s" % (e.args[0],e.args[1])
    		con.rollback()
    		#sys.exit(1)
    
	finally:    
       		cur.close() 
        	con.close()
		del cur
		del con
