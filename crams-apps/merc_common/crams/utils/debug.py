import pprint


class Debug:
    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4)  # For Debug

    def pprint(self, obj):
        """print."""
        if not hasattr(self, 'pp'):
            pass
        self.pp.pprint(obj)
