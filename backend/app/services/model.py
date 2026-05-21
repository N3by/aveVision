import io
import os
import pickle
import time

import numpy as np
import psutil
from PIL import Image

_model = None

# Class labels in training order (index matches model output)
CLASS_LABELS = ["canary", "magpie", "mockingbird", "nightingale", "robin", "tanager"]


def load_model() -> None:
    """Load model from local path (dev) or GCS (production). Called once at startup."""
    global _model
    from app.config import settings

    if settings.local_model_path:
        with open(settings.local_model_path, "rb") as f:
            _model = pickle.load(f)
        print(f"[model] Loaded from local path: {settings.local_model_path}")
    else:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(settings.gcs_bucket_name)
        blob = bucket.blob(settings.model_blob_name)
        model_bytes = blob.download_as_bytes()
        _model = pickle.loads(model_bytes)
        print(f"[model] Loaded from gs://{settings.gcs_bucket_name}/{settings.model_blob_name}")


# Keep old name as alias so existing lifespan call still works
load_model_from_gcs = load_model


def is_model_loaded() -> bool:
    return _model is not None


def run_inference(image_bytes: bytes) -> dict:
    """Run classification on raw image bytes.
    Returns: { predicted_class, confidence, latency_ms, ram_mb, cpu_percent }
    """
    if _model is None:
        raise RuntimeError("Model not loaded")

    process = psutil.Process(os.getpid())
    ram_before = process.memory_info().rss / 1024 / 1024
    start = time.perf_counter()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img_array = np.array(image, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # (1, 224, 224, 3)

    probabilities = _model.predict(img_array, verbose=0)  # (1, 6)
    class_idx = int(np.argmax(probabilities[0]))
    confidence = float(probabilities[0][class_idx])
    predicted_class = CLASS_LABELS[class_idx]

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    ram_after = process.memory_info().rss / 1024 / 1024

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "latency_ms": elapsed_ms,
        "ram_mb": round(max(ram_after - ram_before, 0.0), 2),
        "cpu_percent": round(psutil.cpu_percent(interval=None), 1),
    }
