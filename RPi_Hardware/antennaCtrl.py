import basePositional
import mobilePositional
import deviceManager
import time
from pynmeagps import NMEAMessage, nmeahelpers
import math

dm = deviceManager.DeviceManager()
basePosition = basePositional.BasePosition(dm)
mobilePosition = mobilePositional.MobilePosition(dm)
antennaConnection = dm.antenna
antenna = None
bearing = 0


def getBearing(posFrom : NMEAMessage, posTo : NMEAMessage):
    return nmeahelpers.bearing(posFrom.lat, posFrom.lon, posTo.lat, posTo.lon)


while True:
    mobilePos = mobilePosition.position
    basePos = basePosition.position
    
    if mobilePos is not None and basePos is not None:
        bearing = getBearing(basePos, mobilePos)

    while antenna == None:
        antenna = antennaConnection.getSerialDevice()
        time.sleep(0.5)

    antenna.send("A" + str(math.trunc(bearing)) + "\n")

    time.sleep(1)
    