
"""
doallgraphs.pyd
JCS 1/27/2013 Version 1.0

This program runs all the graphs 
"""

from datetime import datetime, timedelta
import sys
import time




sys.path.append('./datacollect')
sys.path.append('./graphprep')
sys.path.append('./hardware')
sys.path.append('./housekeeping')

import powersupplygraph
import systemstatusgraph
import solarwindgraph
import environmentalgraph
import environmentalgraph2
import environcolor
import batterywatchdogcurrentgraph 
import batterywatchdogvoltagegraph
import powersupplyvoltagesgraph 
import windpowergraph 
import raingraph 




def doallgraphs(location,days, maindelay):


	print("doallgraphs source:%s days:%s delay:%i" % (location,days,maindelay))
	print("sleeping :",maindelay)
	time.sleep(maindelay)
	print("doallgraphs running now")


	delay =1 
	powersupplygraph.powersystemsupplygraph(location,days,delay)    
	powersupplyvoltagesgraph.powersystemsupplyvoltagegraph(location,days, delay)    
	systemstatusgraph.systemstatusgraph(location,days,delay)    


	environmentalgraph.environmentalgraph(location,days, delay)    
	environmentalgraph2.environmentalgraph2(location,days,delay)    
	environcolor.environcolor(location,days,delay)    
	batterywatchdogcurrentgraph.batterywatchdogcurrentgraph(location,days,delay)    
	batterywatchdogvoltagegraph.batterywatchdogvoltagegraph(location,days,delay)    
	solarwindgraph.solarwindgraph(location,days,delay)    
	windpowergraph.windpowergraph(location,days,delay)    
	raingraph.raingraph(location,days,delay)    


