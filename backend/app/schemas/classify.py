from pydantic import BaseModel


class Metrics(BaseModel):
    latency_ms: int
    ram_mb: float
    cpu_percent: float


class ClassifyResponse(BaseModel):
    especie: str
    nombre_cientifico: str
    confianza: float
    descripcion: str
    datos_curiosos: list[str]
    metrics: Metrics
