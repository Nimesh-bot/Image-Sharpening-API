import shutil
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import cv2
import numpy as np
import time
import os

app = FastAPI()
app.mount("/output", StaticFiles(directory="output"), name="output")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/sharpen")
async def sharpen_image(file: UploadFile):
    # Reading the image from the request
    image_file = await file.read()
    img = cv2.imdecode(np.frombuffer(image_file, np.uint8), cv2.IMREAD_UNCHANGED)

    # Gaussian kernel
    gaussian_blur = cv2.GaussianBlur(img, (5,5), 2, 2)

    # Sharpening using addWeighted()
    sharpened = cv2.addWeighted(img, 7.5, gaussian_blur, -6.5, 0)

    # Create a unique folder based on the current time
    folder_name = str(int(time.time()))
    os.makedirs('./output/' + folder_name, exist_ok=True)

    # Save the original and sharpened images in the folder
    cv2.imwrite('./output/' + folder_name + '/original.jpg', img)
    cv2.imwrite('./output/' + folder_name + '/sharpened.jpg', sharpened)

    return {"message": "Image sharpened successfully", "sharpened_path": 'http://127.0.0.1:8000/output/' + folder_name + '/sharpened.jpg'}

@app.get("/results")
def get_results():
    # Get a list of all subdirectories in the output directory
    folders = [f for f in os.listdir('./output') if os.path.isdir(os.path.join('./output', f))]
    return {"results": folders}

@app.delete("/results/{folder_name}")
async def delete_folder(folder_name: str):
    # Validate the folder name
    if not folder_name:
        raise HTTPException(status_code=400, detail="Folder name is required.")
    folder_initial_path = os.path.join(os.getcwd())
    folder_path = os.path.join(folder_initial_path, 'output/', folder_name)
    print(folder_path)
    print(os.path.exists(folder_path))
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Folder does not exist.")

    # Delete the folder
    try:
        shutil.rmtree(folder_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to delete folder: {e}")

    return {"message": f"Folder '{folder_name}' deleted successfully"}

@app.delete('/results')
async def delete_all_folders():
    # Delete all folders in the output directory
    try:
        shutil.rmtree('./output')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to delete folder: {e}")

    # Create a new output directory
    os.makedirs('./output', exist_ok=True)

    return {"message": "All folders deleted successfully"}
    
# python -m uvicorn app:app --reload