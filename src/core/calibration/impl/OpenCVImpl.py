from calibration.common import *
import cv2

class _Impl(CalibrationModule):
    def calibrate(self, input: CalibrationInput) -> CalibrationData:
        objectPoints = []
        imgPoints = []
        for obs in input.observations:
            objectPoints.append(obs.object_points)
            imgPoints.append(obs.img_points)
        camera_matrix = input.seed.getSeedMat()
        dist_coefs = input.seed.getSeedDist()

        #TODO: Figure out a better way to do this
        if input.useSeed:
            rms, camera_matrix, dist_coefs, _, _ = cv2.calibrateCamera(
                objectPoints,
                imgPoints,
                input.size,
                camera_matrix,
                dist_coefs,
                None,
                None,
                flags=cv2.CALIB_USE_INTRINSIC_GUESS
            )
            return CalibrationData(
                input.size,
                camera_matrix.tolist(),
                dist_coefs.tolist(),
                rms
            )
        rms, camera_matrix, dist_coefs, _, _ = cv2.calibrateCamera(
            objectPoints,
            imgPoints,
            input.size,
            camera_matrix,
            dist_coefs,
            None,
            None
        )
        return CalibrationData(
            input.size,
            camera_matrix.tolist(),
            dist_coefs.tolist(),
            rms
        )
    
export = _Impl()