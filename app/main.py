from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import joblib
import pandas as pd
import os

from app.models.crop import CropInput

from app.models.user import UserLogin
from app.utils.security import verify_password
from app.utils.jwt import create_access_token

app = FastAPI(title="KrishiDeep Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. Change this for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# LOAD ML MODEL
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "crop_model.pkl")
model = joblib.load(model_path)

import json
try:
    import tensorflow as tf
    disease_model_path = os.path.join(BASE_DIR, "plant_disease_model.h5")
    classes_path = os.path.join(BASE_DIR, "disease_classes.json")
    
    if os.path.exists(disease_model_path) and os.path.exists(classes_path):
        # Fix for TensorFlow/Keras version mismatch between Kaggle and local Windows machine
        class CustomDepthwiseConv2D(tf.keras.layers.DepthwiseConv2D):
            def __init__(self, **kwargs):
                kwargs.pop('groups', None)
                super().__init__(**kwargs)
                
        disease_model = tf.keras.models.load_model(
            disease_model_path,
            custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D},
            compile=False
        )
        with open(classes_path, "r") as f:
            disease_classes = json.load(f)
    else:
        disease_model = None
        disease_classes = None
except ImportError:
    disease_model = None
    disease_classes = None

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"status": "KrishiDeep backend is running"}

# =========================
# CROP PREDICTION API
# =========================
@app.post("/predict")
def predict_crop(data: CropInput):
    input_df = pd.DataFrame([{
        "N": data.N,
        "P": data.P,
        "K": data.K,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "ph": data.ph,
        "rainfall": data.rainfall
    }])

    prediction = model.predict(input_df)[0]

    return {
        "predicted_crop": prediction,
        "message": "Prediction generated using trained ML model"
    }

# =========================
# DISEASE DETECTION API
# =========================
@app.post("/predict-disease")
async def predict_disease(file: UploadFile = File(...)):
    if disease_model is None or disease_classes is None:
        return {
            "filename": file.filename,
            "predicted_disease": "Model Not Loaded",
            "message": "Please drop plant_disease_model.h5 and disease_classes.json into the app folder and restart server."
        }

    image = Image.open(file.file).convert("RGB")
    # Must match the size we trained with (224x224)
    image = image.resize((224, 224))
    
    img_array = np.array(image)
    # We used rescale=1./255 during training
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    assert disease_model is not None
    assert disease_classes is not None

    # Inference!
    predictions = disease_model.predict(img_array)
    class_idx = str(np.argmax(predictions[0]))
    confidence = float(np.max(predictions[0]))

    # Map the numerical prediction to the disease string using the JSON mapping
    disease = disease_classes.get(class_idx, "Unknown Disease")

    return {
        "filename": file.filename,
        "predicted_disease": disease,
        "confidence": confidence,
        "message": "Prediction generated using Deep Learning CNN"
    }

# =========================
# LOGIN API
# =========================
FAKE_USER_DB = {
    "mahima@gmail.com": {
        "email": "mahima@gmail.com",
        "password": "$2b$12$examplehashedpassword"
    }
}

@app.post("/login")
def login(user: UserLogin):
    db_user = FAKE_USER_DB.get(user.email)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
