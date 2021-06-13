import os
import cv2
import numpy as np
from PIL import Image


# To train every images of the student
def get_image(paths):
    image_paths = [os.path.join(paths, f) for f in os.listdir(paths)]
    face = []
    ids = []
    for image_path in image_paths:
        face_img = Image.open(image_path).convert('L')
        face_np = np.array(face_img, 'uint8')
        id = int(os.path.split(image_path)[-1].split('.')[1])
        print('TRAINER PY:::::::::::', id)
        face.append(face_np)
        ids.append(id)
        cv2.waitKey(10)
    return np.array(ids), face
