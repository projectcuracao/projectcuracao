#
#
# configuration file - contains customization for exact system
# JCS 11/8/2013
#

mailUser = "YourUserName"
mailPassword = "YourPassword"

databasePassword = "databasePassword"

notifyAddress = "YourName@YourDomain.com"

fromAddress = "YourFrom@YourFromDomain.com"


# main sensor / action loop constants

PI_BATTERY_SHUTDOWN_THRESHOLD = 3.706 # 20%
PI_BATTERY_STARTUP_THRESHOLD = 3.839 # 30%

INSIDE_TEMPERATURE_PI_SHUTDOWN_THRESHOLD = 49.33 # 110
INSIDE_TEMPERATURE_PI_STARTUP_THRESHOLD = 37.78  # 100


INSIDE_HUMIDITY_PI_SHUTDOWN_THRESHOLD = 98.0 
INSIDE_HUMIDITY_PI_STARTUP_THRESHOLD = 93.0

FAN_ON_TEMPERATURE = 35.0 # 95 F
FAN_OFF_TEMPERATURE = 30.0 # 86 F

FAN_ON_HUMIDITY = 85.0  
FAN_OFF_HUMIDITY = 70.0 

PI_START_TIME = "10:00:00" # UTC
PI_SHUTDOWN_TIME = "22:30:00" #UTC
PI_MIDNIGHT_WAKEUP_SECONDS_LENGTH = 3600.0   # one hour

PI_MIDNIGHT_WAKEUP_THRESHOLD = 3.971   # 60%

enableShutdowns = 1 
