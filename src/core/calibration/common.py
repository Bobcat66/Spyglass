from abc import ABC, abstractmethod
from dataclasses import dataclass,asdict
import numpy as np
from typing import Tuple, List, Self
import json

# This module contains the portions of the calibration toolkit that are platform-agnostic. 

# SamuraiSight only supports ChArUco boards

@dataclass
class BoardObservation:
    object_points: np.typing.NDArray[np.float64]
    img_points: np.typing.NDArray[np.float64]
    weights: np.typing.NDArray[np.float64]

@dataclass
class Seed:
    fx: float
    fy: float
    cx: float
    cy: float
    k1: float
    k2: float
    p1: float
    p2: float
    k3: float

    def getSeedMat(self) -> np.typing.NDArray[np.float64]:
        return np.array([
            [self.fx,0.00000,self.cx],
            [0.00000,self.fy,self.cy],
            [0.00000,0.00000,1.00000]
        ])
    
    def getSeedDist(self) -> np.typing.NDArray[np.float64]:
        return np.array([self.k1,self.k2,self.p1,self.p2,self.k3])


@dataclass
class CalibrationInput:
    observations: List[BoardObservation]
    size: Tuple[int,int]
    seed: Seed
    useSeed: bool

@dataclass
class CalibrationData:
    size: Tuple[int,int]
    matrix: List[List[float]] #These have to be basic lists in order to keep them JSON-serializable
    dist_coeffs: List[float]
    avg_reproject_err: float

    def getNumpyMat(self) -> np.typing.NDArray[np.float64]:
        return np.array(self.matrix,dtype=np.float64)
    
    def getNumpyDistCoeffs(self) -> np.typing.NDArray[np.float64]:
        return np.array(self.dist_coeffs,dtype=np.float64)
    
    @classmethod
    def dumpJson(cls,cdat: Self) -> str:
        return json.dumps(asdict(cdat))
    
    @classmethod
    def loadJson(cls,jdat: str) -> Self:
        jdict: dict = json.loads(jdat)
        return cls(
            jdict.get("size"),
            jdict.get("matrix"),
            jdict.get("dist_coeffs"),
            jdict.get("avg_reproject_err")
        )




class CalibrationModule(ABC):
    @abstractmethod
    def calibrate(self, input: CalibrationInput) -> CalibrationData:
        raise NotImplementedError()

        




    
    


    