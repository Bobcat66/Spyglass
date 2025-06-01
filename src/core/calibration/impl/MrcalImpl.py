# Copyright (c) Jesse Kane
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

from calibration.common import *
import mrcal

class _Impl(CalibrationModule):
    def calibrate(self, input: CalibrationInput) -> CalibrationData:
        raise NotImplementedError("Mrcal integration is still WIP")
    
export = _Impl()