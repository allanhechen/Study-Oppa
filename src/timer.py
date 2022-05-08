from enum import Enum

class TimerStatus(Enum):
    INITIALIZED = 1
    RUNNING = 2
    STOPPED = 3

class Timer:

    def __init__(self):
        self.status = TimerStatus.INITIALIZED
    
    def start(self):
        self.status = TimerStatus.RUNNING

    def stop(self):
        self.status = TimerStatus.STOPPED

    def getStatus(self):
        return self.status