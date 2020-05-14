import time

def tic():
    tic.start = time.perf_counter()

def toc():
    elapsed_seconds = time.perf_counter() - tic.start
    return elapsed_seconds # fractional

# So I can nest tic/toc.
class Timer():
    def __init():
        self.start = time.perf_counter()

    @property
    def tic(self):
        self.start = time.perf_counter()

    @property
    def toc(self):
        elapsed_seconds = time.perf_counter() - self.start
        return elapsed_seconds # fractional
    
