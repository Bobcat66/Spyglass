import threading

class AtomicInt():
    def __init__(self, value: int = 0):
        self.__value: int = value
        self.__lock: threading.Lock = threading.Lock()
    
    def get() -> int:
        with self.__lock:
            return self.__value
    
    def set(self, value: int) -> None:
        with self.__lock:
            self.__value = value
            return None

    def increment(self) -> int: 
        with self.__lock:
            self.__value += 1
            return self.__value

    def decrement(self) -> int:
        with self.__lock:
            self.__value -= 1
