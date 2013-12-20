import time

class TimeIt():
    """Decorator to time a function execution"""
    time = 0
    def __init__(self, f):
        self.time = 0
        self.f = f

    def __call__(self):
        self.time = time.time()
        self.f()
        print "%s took %0.3fs to execute" % (str(self.f.__name__), time.time() - self.time)
