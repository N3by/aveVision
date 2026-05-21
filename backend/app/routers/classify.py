from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas.classify import ClassifyResponse, Metrics
from app.services.firebase import verify_token
from app.services.model import run_inference
from app.data.species_data import get_species_info

router = APIRouter(tags=["classify"])


@router.post("/classify", response_model=ClassifyResponse)
async def classify_image(
    file: UploadFile = File(...),
    token: dict = Depends(verify_token),
) -> ClassifyResponse:
    image_bytes = await file.read()
    inference = run_inference(image_bytes)
    species = get_species_info(inference["predicted_class"])

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
