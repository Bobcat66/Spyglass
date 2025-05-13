
import os
from calibration.common import CalibrationModule
from typing import Dict
import logging
mrcal: bool = os.getenv("MRCAL") == "true"

logger = logging.getLogger(__name__)

_modules: Dict[str,CalibrationModule] = {}

# Load opencv module
from calibration.impl import OpenCVImpl
_modules["opencv"] = OpenCVImpl.export

# Optionally load mrcal module
if mrcal:
    from calibration.impl import MrcalImpl
    _modules["mrcal"] = MrcalImpl.export

def getModule(modname: str) -> CalibrationModule:
    module = _modules.get(modname)
    if module is None:
        logger.warning("module %s is not loaded",modname)
    return module

def getMrcal() -> CalibrationModule:
    return getModule("mrcal")

def getOpenCV() -> CalibrationModule:
    return getModule("opencv")
