from deepface import DeepFace
import cv2
import numpy as np

backends = [
    'opencv', 'ssd', 'dlib', 'mtcnn', 'fastmtcnn',
    'retinaface', 'mediapipe', 'yolov8', 'yolov11s',
    'yolov11n', 'yolov11m', 'yunet', 'centerface',
]
detector = backends[0]
align = True

face_objs = DeepFace.extract_faces(
  img_path = "img.jpg", detector_backend = detector, align = align
)


face_img = face_objs[0]["face"]

  # Chuyển đổi ảnh từ RGB [0,1] sang BGR [0,255]
face_img_bgr = cv2.cvtColor((face_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
scale_percent = 500  # Resize xuống 50%
width = int(face_img_bgr.shape[1] * scale_percent / 100)
height = int(face_img_bgr.shape[0] * scale_percent / 100)
resized_img = cv2.resize(face_img_bgr, (width, height), interpolation=cv2.INTER_LINEAR)
cv2.imshow("win", resized_img)
cv2.waitKey(0)
# for i, face in enumerate(face_objs):
#     face_img = face["face"]
#     # Chuyển đổi ảnh từ RGB [0,1] sang BGR [0,255]
#     face_img_bgr = cv2.cvtColor((face_img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
#     cv2.imwrite(f"face_{i+1}.jpg", face_img_bgr)