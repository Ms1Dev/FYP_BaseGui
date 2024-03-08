from Interface.process import Process
from typing import List, Union
from oled import Row

class Submenu:

    def __init__(self, label : str, options : List[Union['Submenu', 'Process']]) -> None:
        self.label = label
        self.selected_submenu : Submenu = None
        self.options = options
        self.option_index = 0

    def leftBtnPressed(self):
        if self.selected_submenu:
            self.selected_submenu.leftBtnPressed()
        elif self.option_index > 0:
            self.option_index -= 1

    def middleBtnPressed(self):
        if self.selected_submenu:
            self.selected_submenu.middleBtnPressed()
        elif self.option_index < (len(self.options) - 1):
            self.option_index += 1
    
    def rightBtnPressed(self):
        if self.selected_submenu:
            self.selected_submenu.rightBtnPressed()
        else:
            self.selected_submenu = self.options[self.option_index].selected()


    def leftBtnHeld(self):
        self.selected_submenu = None

    def middleBtnHeld(self):
        if self.selected_submenu:
            self.selected_submenu.middleBtnHeld()
        else:
            pass
    
    def rightBtnHeld(self):
        if self.selected_submenu:
            self.selected_submenu.rightBtnHeld()
        else:
            pass

    def selected(self):
        return self
    

    def getRows(self):
        if self.selected_submenu:
            return self.selected_submenu.getRows()
        rows = [Row(self.label, filled=True)]
        list_offset = int(self.option_index / 4) * 4
        for i, option in enumerate(self.options):
            if i < list_offset:
                continue
            outline = False
            if i == self.option_index:
                outline = True
            rows.append(Row(option.label, outline=outline))
        return rows