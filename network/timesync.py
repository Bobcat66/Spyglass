# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

from time import perf_counter
from utils.atomic import AtomicInt

fpgaSyncTime: AtomicInt = AtomicInt()
localSyncTime: AtomicInt = AtomicInt()
offset: AtomicInt = AtomicInt()

def sync(fpgatime: int) -> None:
    fpgaSyncTime.set(fpgatime)
    localSyncTime.set(int(perf_counter() * 1e6))
    offset.set(fpgaSyncTime.get() - localSyncTime.get())

def getFPGA() -> int:
    return int(perf_counter() * 1e6) + offset.get()

#TODO: Fix this