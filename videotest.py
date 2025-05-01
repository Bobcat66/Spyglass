import cv2
from pipeline import tagdetector
from pipeline.annotator import drawFiducials
if __name__ == "__main__":
    cam = cv2.VideoCapture(0)
    result, image = cam.read()
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        detections = tagdetector.detectCV_BGR(frame)
        drawFiducials(frame, detections)
        cv2.imshow('Webcam Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()