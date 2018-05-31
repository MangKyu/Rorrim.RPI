import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX

def faceDetect():
    face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_alt2.xml")
   
    try:
        cap = cv2.VideoCapture(0)
    except:
        print("cam loading failed")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 2, 0, (30, 30))

        if len(faces) == 1:
            start_x = faces[0][0] - int(faces[0][2]*0.3)
            end_x = faces[0][0] + int(faces[0][2]*1.3)
            start_y = faces[0][1] - int(faces[0][3]*0.3)
            end_y = faces[0][1] + int(faces[0][3]*1.3)
            if start_x < 0:
                start_x = 0
            if start_y < 0:
                start_y = 0
            if end_x >= len(frame[0]):
                end_x = len(frame[0])
            if end_y >= len(frame):
                end_y = len(frame)
            
            if end_x - start_x >= 100 and end_y - start_y >= 100:
                f = frame[start_y:end_y, start_x:end_x]
                cv2.imwrite('.test.jpg', f)

    cap.release()
    cv2.destroyAllWindows()

faceDetect()
