import os
import shutil
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_results():
    # Send a GET request to the get_results endpoint
    response = client.get("/results")

    # Check the response status code
    assert response.status_code == 200

    # Check the response content
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

def test_delete_folder():
    # Create a temporary folder for testing
    folder_name = "test_folder"
    os.makedirs(f"./output/{folder_name}", exist_ok=True)

    # Send a DELETE request to the delete_folder endpoint
    response = client.delete(f"/results/{folder_name}")

    # Check the response status code
    assert response.status_code == 200

    # Check if the folder is deleted
    assert not os.path.exists(f"./output/{folder_name}")
