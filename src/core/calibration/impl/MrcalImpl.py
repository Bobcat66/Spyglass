from calibration.common import *

class _Impl(CalibrationModule):
    def calibrate(self, input: CalibrationInput) -> CalibrationData:
        raise NotImplementedError("Mrcal is still WIP")
    
export = _Impl()