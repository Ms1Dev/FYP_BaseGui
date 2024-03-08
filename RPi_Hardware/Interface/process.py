

class Process():
    def __init__(self, label : str, task = None) -> None:
        self.label = label
        self.task = task

    def selected(self):
        self.performTask()

    def performTask(self):
        self.task()
