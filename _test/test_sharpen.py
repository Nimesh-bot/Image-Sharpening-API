import io
from fastapi.testclient import TestClient
from requests_toolbelt.multipart.encoder import MultipartEncoder
from app import app
import cv2
import numpy as np
import os

client = TestClient(app)

def test_sharpen_image():
    # Load a sample image
    image_name = 'original.jpg'
    current_directory = os.path.dirname(os.path.abspath(__file__)) 
    base_directory = os.path.dirname(os.path.abspath(current_directory))
    print(base_directory)
    image_path = os.path.join(base_directory, "output", "1681976981", image_name)
    img = cv2.imread(image_path)

    # Convert the image to bytes
    _, image_bytes = cv2.imencode('.jpg', img)
    image_file = io.BytesIO(image_bytes.tobytes())

    # Define the test payload
    form_data = MultipartEncoder(
        fields={
            'file': ('image.jpg', image_file),
            'kernelMatrixHeight': '5',
            'kernelMatrixWidth': '5',
            'sigmaX': '1.0',
            'sigmaY': '0.0',
            'contributionOriginalImage': '0.5',
            'contributionBlurryImage': '0.5',
            'gamma': '1.0',
            'base_url': 'http://127.0.0.1:8000'
        }
    )

    # delete all T-T

    headers = {'Content-Type': form_data.content_type}

    # Send a POST request to the sharpen_image endpoint
    response = client.post("/sharpen", data=form_data.to_string(), headers=headers)
    
    # Check the response status code
    assert response.status_code == 200

    # Check the response message
    assert response.json()["message"] == "Image sharpened successfully"

    # Check if the sharpened image is saved
    sharpened_path = response.json()["sharpened_path"]
    assert sharpened_path.startswith('http://127.0.0.1:8000/output/')
    assert sharpened_path.endswith('/sharpened.jpg')

    # Load the sharpened image
    sharpened_img = cv2.imread(sharpened_path)


