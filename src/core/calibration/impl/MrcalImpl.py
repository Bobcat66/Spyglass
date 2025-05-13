from calibration.common import *
import mrcal

class _Impl(CalibrationModule):
    def calibrate(self, input: CalibrationInput) -> CalibrationData:
        raise NotImplementedError("Mrcal is still WIP")
    
export = _Impl()