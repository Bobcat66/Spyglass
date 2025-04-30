# Copyright (c) FRC 1076 PiHi Samurai
# You may use, distribute, and modify this software under the terms of
# the license found in the root directory of this project

import numpy as np
import cv2

def ndarrayToMat(ndarray: np.typing.NDArray[np.uint8]) -> cv2.Mat:
    """
    Convert a numpy ndarray to a cv2 Mat object.
    :param ndarray: The numpy array to convert.
    :return: The converted cv2 Mat object.
    """
    return cv2.Mat(ndarray)

def matToNdarray(mat: cv2.Mat) -> np.typing.NDArray[np.uint8]:
    """
    Convert a cv2 Mat object to a numpy ndarray.
    :param mat: The cv2 Mat object to convert.
    :return: The converted numpy ndarray.
    """
    return np.array(mat, dtype=np.uint8)