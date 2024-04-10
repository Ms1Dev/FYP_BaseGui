from position import Position
import os
import math
import csv

class CoordinateLogger:
    dirLoc = "/home/michael-zwann/coordinate_log/"
    filePrefix = "data_"
    fileExt = ".csv"


    def __init__(self) -> None:
        fileId = 0

        try:
            for file in os.listdir(self.dirLoc):
                id = file.replace(self.filePrefix, "")
                id = id.replace(self.fileExt, "")
                fileId = max(int(id), fileId)           
        except OSError as e:
            os.makedirs(self.dirLoc)

        fileId += 1

        self.fileName = self.dirLoc + self.filePrefix + str(fileId) + self.fileExt
    

    def update(self, posFrom : Position, posTo : Position, distance : float):
        try:
            with open(self.fileName, "a") as dataFile:
                csvWriter = csv.writer(dataFile)
                csvWriter.writerow((posFrom.getLatest(), posTo.getLatest(), distance))
        except Exception as e:
            print("Failed to store coordinate value - ", e)
