import time

def releaseGIL():
    time.sleep(0) # time.sleep releases the GIL