from Interface.task import Task
from Interface.option import Option
from typing import List
from oled import Row

class Screen(Option):

    def __init__(self, label : str, options : List[Option]) -> None:
        super().__init__(label)
        self.selected_screen : Screen = None
        self.options = options
        self.option_index = 0

    def leftBtnPressed(self):
        if self.selected_screen:
            self.selected_screen.leftBtnPressed()
        elif self.option_index > 0:
            self.option_index -= 1

    def middleBtnPressed(self):
        if self.selected_screen:
            self.selected_screen.middleBtnPressed()
        elif self.option_index < (len(self.options) - 1):
            self.option_index += 1
    
    def rightBtnPressed(self):
        self.selected_screen = self.options[self.option_index].selected(self)

    def leftBtnHeld(self):
        self.selected_screen = None

    def middleBtnHeld(self):
        if self.selected_screen:
            self.selected_screen.middleBtnHeld()
        else:
            pass
    
    def rightBtnHeld(self):
        if self.selected_screen:
            self.selected_screen.rightBtnHeld()
        else:
            pass

    def selected(self, screen):
        return self
    

    def getRows(self):
        if self.selected_screen:
            return self.selected_screen.getRows()
        rows = [Row(self.label, filled=True)]
        for i, option in enumerate(self.options):
            outline = False
            if i == self.option_index:
                outline = True
            rows.append(Row(option.label, outline=outline))
        return rows