

class Option:
    def __init__(self, label : str) -> None:
        self.label = label

    def selected(self, option):
        return option