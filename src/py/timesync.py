from time import perf_counter
from atomic import AtomicInt

fpgaSyncTime: AtomicInt = AtomicInt()
localSyncTime: AtomicInt = AtomicInt()
offset: AtomicInt

def sync(fpgatime: int) -> None:
    fpgaSyncTime.set(fpgatime)
    localSyncTime.set(int(perf_counter() * 1e6))
    offset.set(fpgaSyncTime.get() - localSyncTime.get())

def getFPGA() -> int:
    return int(perf_counter() * 1e6) + offset.get()

#TODO: Fix this