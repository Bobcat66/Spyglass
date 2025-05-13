from calibration.common import *
import cv2

class _Impl(CalibrationModule):
    def calibrate(self, input: CalibrationInput) -> CalibrationData:
        objectPoints = []
        imgPoints = []
        for obs in input.observations:
            objectPoints.append(obs.object_points)
            imgPoints.append(obs.img_points)
        camera_matrix = np.array([
            [input.fx_seed,0.00000000000,input.cx_seed],
            [0.00000000000,input.fy_seed,input.cy_seed],
            [0.00000000000,0.00000000000,1.00000000000]
        ])
        dist_coefs = input.dist_coeffs_seed.copy()
        rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(
            objectPoints,
            imgPoints,
            input.size,
            camera_matrix,
            dist_coefs,
            None,
            None,
            cv2.CALIB_USE_INTRINSIC_GUESS
        )
        return CalibrationData(
            input.size,
            camera_matrix.tolist(),
            dist_coefs.tolist(),
            rms
        )
    
export = _Impl()