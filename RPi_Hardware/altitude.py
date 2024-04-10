from collections import deque
from pvlib import atmosphere

class Altitude:
    def __init__(self, mode = "avg"):
        self.altitude_history = deque()
        self.sample_size = 100
        self.mode = mode
        self.latest_altitude = None
    

    def newData(self, pressure):
        altitude = self.altFromPressure(pressure)
        if altitude is not None:
            self.altitude_history.appendleft(altitude)
            self.resizeData() 
            self.latest_altitude = self.getAltitude()
        

    def altFromPressure(self, pressure):
        if pressure == "-9.99":
            return
        try:
            pressure = float(pressure)
            pressure = pressure * 100 # convert to pa
            return atmosphere.pres2alt(pressure)
        except:
            pass

    def avgLocation(self):
        self.mode = "avg"

    def liveLocation(self):
        self.mode = "live"

    def resizeData(self):
        while(len(self.altitude_history) > self.sample_size):
            self.altitude_history.pop()


    def setSampleSize(self, size):
        self.sample_size = size


    def getAltitude(self):
        if self.mode == "avg":
            return self.getAverage()
        if self.mode == "live":
            try:
                return self.altitude_history[0]
            except:
                return None
    

    def getAverage(self):
        try:
            alt = 0
            count = 0
            for altitude in self.altitude_history:
                alt += altitude
                count += 1
            if count == 0:
                return None
            alt /= count
            return alt
        except:
            return None


    def getVerticalDistance(self, altitudeTo, offset = 0):
        try:
            alt_from = self.latest_altitude
            alt_to = altitudeTo.latest_altitude
            if alt_from is not None and alt_to is not None:
                return (alt_from - alt_to - offset)
            return None
        except:
            return None