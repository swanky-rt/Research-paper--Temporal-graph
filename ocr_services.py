from flask import Flask, request, jsonify   # for creating the API service.
import base64
import cv2
import numpy as np
import pytesseract

app = Flask(__name__)   # Starts the  Flask app so it can listen for API calls.


# Decode base64 image to OpenCV format
def decode_image(base64_string):                   # Takes a base64 image string and convert it into a usable image format with OpenCV
    image_bytes = base64.b64decode(base64_string)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


# Extract text using Tesseract
def extract_text_from_image(image):                 # OCR works better on grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Converts the image to grayscale
    text = pytesseract.image_to_string(gray)        # Extracts all text from it
    return text.strip()                             # Cleans it up a bit (removing leading/trailing whitespace)

@app.route('/ocr-name', methods=['POST'])    # This defines the endpoint /ocr-name, which will accept POST requests only.

def ocr_name():
    data = request.get_json()      # Reads the incoming JSON and extracts the base64-encoded ID image from the "idImageBase64" field.
    id_image_b64 = data.get("idImageBase64")

    if not id_image_b64:
        return jsonify({"nameText": "", "error": "Missing image"}), 400        # If the image is missing from the request, return an error response with status 400 Bad Request.

    image = decode_image(id_image_b64)
    extracted_text = extract_text_from_image(image)  # Decodes the base64 and extracts text using the helper functions we wrote.

    return jsonify({"nameText": extracted_text})   # Sends back the recognized text (usually includes the person's name and other text from the ID).

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)  # Starts the Flask app and makes it available on port 5002, listening on all network interfaces (0.0.0.0).