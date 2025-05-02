from processes.VisionWorker import VisionWorker
from configuration.config_types import *
import cscore
import robotpy_apriltag as apriltag
import ntcore
import time
from network import ntmanager
if __name__ == "__main__":
     # Initialize NetworkTables
    inst: ntcore.NetworkTableInstance = ntcore.NetworkTableInstance.getDefault()
    inst.startServer("10.10.76.2")
    inst.startClient4("SamsightClient")
    ntmanager.initialize("Test",inst)
    camConfig = CameraConfig(
        "webcam",
        0,
        True,
        np.array([
            [
                979.1087360312252,
                0,
                608.5591334099096
            ],
            [
                0,
                979.8457780935689,
                352.9815581130428
            ],
            [
                0,
                0,
                1
            ]
        ], dtype=np.float64),
        np.array([
            0.09581952042360092,
            -0.2603932345361037,
            0.0035795949814343524,
            -0.005134231272255606,
            0.19101200082384226
        ], dtype=np.float64),
        cscore.VideoMode.PixelFormat.kMJPEG,
        1280,
        720,
        60
    )
    fieldConfig = FieldConfig(
        tag_size=0.1651,
        layout=apriltag.AprilTagFieldLayout("resources/fields/2025-reefscape-welded.json"),
        family="tag36h11"
    )
    pipConfig = PipelineConfig(
        "test_pipe",
        "apriltag",
        "webcam",
        True,
        True,
        8000,
        8001,
        None,
        None,
        None,
        None
    )
    worker = VisionWorker(fieldConfig,camConfig,pipConfig)
    print(cscore.UsbCamera.enumerateUsbCameras())
    
    worker.start()
    while True:
        #Yield to the worker thread
        time.sleep(60)
    print("END")
    