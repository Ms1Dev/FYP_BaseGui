
from Interface.option import Option

class Task(Option):
    def __init__(self, label : str) -> None:
        super().__init__(label)

    def selected(self, screen):
        self.performTask()
        return screen

    def performTask(self):
        print(self.label)