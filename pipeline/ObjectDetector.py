from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_path: str):
        """
        Initialize the ObjectDetector with a YOLO model.

        :param model_path: Path to the YOLO model file.
        """
        self._model = YOLO(model_path,'detect')