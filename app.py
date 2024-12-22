# uvicorn app:app --reload --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem --timeout-keep-alive 120

import time
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
import os
from starlette.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# List of allowed origins, adjust based on your needs
origins = [
    "http://localhost",  # Allow localhost
    "http://localhost:3000",  # Example for React app running on port 3000
    "*"
]

# Add CORSMiddleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows the listed origins to access your API
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Directory to save uploaded files
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/xyz")
async def upload_file(metadata: str = Form(...), image: UploadFile = File(...)):
    try:
        # Save the uploaded file
        parsed_metadata = json.loads(metadata)
        file_location = os.path.join(UPLOAD_FOLDER, image.filename)
        with open(file_location, "wb") as buffer:
            buffer.write(await image.read())

        # Process the file
        new_file_name = os.path.join(UPLOAD_FOLDER, "processed_" + image.filename)
        processed_file_location = process_file(file_location, new_file_name)

        return FileResponse(processed_file_location, media_type='application/octet-stream')
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# TOBE IMPLEMENTED
def process_file(file : str, new_store_location) -> str:
    # Do something with the file
    print(f"Processing file {file}")
    with open(file, "rb") as f:
        data = f.read()
    with open(new_store_location, "wb") as f:
        f.write(data)
        f.write(b"\nThis is a copied script")
    return new_store_location

# Automatically redirect all HTTP traffic to HTTPS
# async def enforce_https(request, call_next):
#     print("Attempting to enforce HTTPS")
#     if request.url.scheme != "https":
#         return {"message": "Only HTTPS connections are allowed"}, 400
#     response = await call_next(request)
#     return response

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}