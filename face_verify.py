
from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np
import face_recognition

app = Flask(__name__)

def decode_image(base64_string):
    image_bytes = base64.b64decode(base64_string)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def compare_faces(id_img, selfie_img):
    try:
        id_face_encodings = face_recognition.face_encodings(id_img)
        selfie_face_encodings = face_recognition.face_encodings(selfie_img)

        if len(id_face_encodings) == 0 or len(selfie_face_encodings) == 0:
            return False

        match = face_recognition.compare_faces([id_face_encodings[0]], selfie_face_encodings[0])[0]
        return match
    except:
        return False



# @app.route('/verify-face', methods=['POST'])  # original
def verify_face():
    data = request.get_json()

    id_image_b64 = data.get("idImageBase64")
    selfie_image_b64 = data.get("selfieImageBase64")

    if not id_image_b64 or not selfie_image_b64:
        return jsonify({"match": False}), 400

    id_img = decode_image(id_image_b64)
    selfie_img = decode_image(selfie_image_b64)

    is_match = compare_faces(id_img, selfie_img)

    return jsonify({"match": is_match})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)