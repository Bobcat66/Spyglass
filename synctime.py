from time import perf_counter
from Atomic import AtomicInt

fpgaEpoch: AtomicInt
localEpoch: AtomicInt
offset: AtomicInt

def sync(int fpgatime) -> None:
    #returns the current timestamp synchronized with the FPGA