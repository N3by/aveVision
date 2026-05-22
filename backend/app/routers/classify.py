import logging

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.request_log import RequestLog
from app.schemas.classify import ClassifyResponse, Metrics
from app.services.firebase import verify_token
from app.services.model import run_inference
from app.data.species_data import get_species_info

logger = logging.getLogger(__name__)
router = APIRouter(tags=["classify"])


@router.post("/classify", response_model=ClassifyResponse)
async def classify_image(
    file: UploadFile = File(...),
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> ClassifyResponse:
    image_bytes = await file.read()
    inference = run_inference(image_bytes)
    species = get_species_info(inference["predicted_class"])

    log = RequestLog(
        user_id=token["uid"],
        image_filename=file.filename,
        predicted_class=inference["predicted_class"],
        confidence=inference["confidence"],
        latency_ms=inference["latency_ms"],
        ram_mb=inference["ram_mb"],
        cpu_percent=inference["cpu_percent"],
    )
    try:
        db.add(log)
        await db.commit()
    except Exception:
        logger.exception("Failed to persist RequestLog for user %s", token["uid"])
        await db.rollback()

    return ClassifyResponse(
        especie=species["especie"],
        nombre_cientifico=species["nombre_cientifico"],
        confianza=inference["confidence"],
        descripcion=species["descripcion"],
        datos_curiosos=species["datos_curiosos"],
        metrics=Metrics(
            latency_ms=inference["latency_ms"],
            ram_mb=inference["ram_mb"],
            cpu_percent=inference["cpu_percent"],
        ),
    )
