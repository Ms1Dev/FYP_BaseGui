from Interface.submenu import Submenu
from oled import Row

class Info(Submenu):

    def __init__(self, label : str, infoGetterMethod) -> None:
        self.label = label
        self.infoGetterMethod = infoGetterMethod
        self.rows = []

    
    def selected(self):
        self.rows = self.infoGetterMethod()
        return self
    

    def getRows(self):
        rows = [Row(self.label, filled=True)]
        rows.extend([Row(row) for row in self.rows])
        return rows
    

class LiveInfo(Info):
    def __init__(self, label : str, rows):
        super().__init__(label, None)
        self.rows = rows

    def selected(self):
        return self
