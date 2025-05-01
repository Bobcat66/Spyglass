from time import perf_counter_ns
import ntcore

def time_us() -> int:
    """
    Get the current time in microseconds.
    """
    return perf_counter_ns() // 1000

def networktime() -> int:
    """
    Get the current network time in microseconds.
    """
    return ntcore._now()