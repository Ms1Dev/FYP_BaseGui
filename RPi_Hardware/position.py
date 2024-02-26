from collections import deque
from pynmeagps import nmeahelpers


class Position:
    def __init__(self):
        self.coordinate_history = deque()
        self.sample_size = 60
        self.mode = "avg"
        self.fixed_location = None
        self.latest_coordinate = None
    

    def newData(self, coordinate):
        self.coordinate_history.appendleft(coordinate)
        if self.fixed_location is None:
            self.fixed_location = coordinate
        self.resizeData() 
        self.latest_coordinate = self.getCoordinate()
        

    def resizeData(self):
        while(len(self.coordinate_history) > self.sample_size):
            self.coordinate_history.pop()


    def setSampleSize(self, size):
        self.sample_size = size


    def fixLocation(self, coordinate = None):
        if coordinate is None:
            self.fixed_location = self.getCoordinate()
        else:
            self.fixed_location = coordinate
        self.mode = "fixed"


    def avgLocation(self):
        self.mode = "avg"


    def liveLocation(self):
        self.mode = "live"


    def getLatest(self):
        return self.latest_coordinate
    

    def getAverage(self):
        try:
            lat = 0
            lon = 0
            count = 0
            for coord in self.coordinate_history:
                lat += coord[0]
                lon += coord[1]
                count += 1
            if count == 0:
                return None
            lat /= count
            lon /= count
            return (lat,lon)
        except:
            return None
    

    def getCoordinate(self):
        if self.mode == "avg":
            return self.getAverage()
        if self.mode == "live":
            try:
                return self.coordinate_history[0]
            except:
                return None
        if self.mode == "fixed":
            return self.fixed_location
    
    
    def getBearingTo(self, position):
        try:
            pos_from = self.latest_coordinate
            pos_to = position.latest_coordinate
            if pos_from is not None and pos_to is not None:
                return nmeahelpers.bearing(pos_from[0], pos_from[1], pos_to[0], pos_to[1])
            return None
        except:
            return None
        

    def getDistanceTo(self, position):
        try:
            pos_from = self.latest_coordinate
            pos_to = position.latest_coordinate
            if pos_from is not None and pos_to is not None:
                return nmeahelpers.planar(pos_from[0], pos_from[1], pos_to[0], pos_to[1])
            return None
        except:
            return None
    

    def getMode(self):
        return self.mode