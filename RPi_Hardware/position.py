from collections import deque



class Position:
    def __init__(self):
        self.coordinate_history = deque()
        self.sample_size = 60
        self.mode = "avg"
        self.fixed_location = None

    
    def newData(self, coordinate):
        self.coordinate_history.appendleft(coordinate)
        if self.fixed_location is None:
            self.fixed_location = coordinate
        self.resizeData() 


    def resizeData(self):
        while(len(self.coordinate_history) > self.sample_size):
            self.coordinate_history.pop()


    def setSampleSize(self, size):
        self.sample_size = size


    def fixLocation(self, coordinate):
        self.fixed_location = coordinate


    def getAverage(self):
        lat = 0
        lon = 0
        count = 0
        for coord in self.coordinate_history:
            lat += coord[0]
            lon += coord[1]
            count += 1
        lat /= count
        lon /= count
        return (lat,lon)
    

    def getCoordinate(self):
        if self.mode == "avg":
            return self.getAverage()
        if self.mode == "live":
            return self.coordinate_history[0]
        if self.mode == "fix":
            return self.fixed_location