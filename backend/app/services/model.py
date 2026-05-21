import io
import os
import pickle
import time

import numpy as np
import psutil
from PIL import Image

_model = None


def load_model_from_gcs() -> None:
    """Download model.pkl from GCS and hold in memory. Called once at startup."""
    global _model
    from google.cloud import storage
    from app.config import settings

    client = storage.Client()
    bucket = client.bucket(settings.gcs_bucket_name)
    blob = bucket.blob(settings.model_blob_name)
    model_bytes = blob.download_as_bytes()
    _model = pickle.loads(model_bytes)
    print(f"[model] Loaded from gs://{settings.gcs_bucket_name}/{settings.model_blob_name}")


def is_model_loaded() -> bool:
    return _model is not None


def run_inference(image_bytes: bytes) -> dict:
    """
    Run classification on raw image bytes.
    Adapt the preprocessing and prediction call to match your model's expected input.
    Returns: { predicted_class, confidence, latency_ms, ram_mb, cpu_percent }
    """
    if _model is None:
        raise RuntimeError("Model not loaded")

    process = psutil.Process(os.getpid())
    ram_before = process.memory_info().rss / 1024 / 1024

    start = time.perf_counter()

    # --- Preprocessing (adapt to your model) ---
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img_array = np.array(image, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # shape: (1, 224, 224, 3)

    # --- Inference ---
    # For sklearn: prediction = _model.predict(img_array)[0]
    # For Keras/TF: probabilities = _model.predict(img_array)[0]; prediction = classes[np.argmax(probabilities)]
    # Adjust the lines below to match your model's output format:
    probabilities = _model.predict(img_array)
    if hasattr(probabilities, '__len__') and len(probabilities.shape) > 1:
        # Multi-class output (Keras-style)
        class_idx = int(np.argmax(probabilities[0]))
        confidence = float(probabilities[0][class_idx])
        # Map index to label if model has classes_ attribute, else use str(class_idx)
        classes = getattr(_model, "classes_", None)
        predicted_class = str(classes[class_idx]) if classes is not None else str(class_idx)
    else:
        # Direct label output (sklearn-style)
        predicted_class = str(probabilities[0])
        confidence = 1.0  # sklearn classifiers don't return confidence by default

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    ram_after = process.memory_info().rss / 1024 / 1024

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "latency_ms": elapsed_ms,
        "ram_mb": round(max(ram_after - ram_before, 0.0), 2),
        "cpu_percent": round(psutil.cpu_percent(interval=None), 1),
    }
