from datetime import datetime
from pydantic import BaseModel


class RequestLogResponse(BaseModel):
    id: int
    user_id: str
    image_filename: str | None
    predicted_class: str | None
    confidence: float | None
    latency_ms: int | None
    ram_mb: float | None
    cpu_percent: float | None
    created_at: datetime | None

    model_config = {"from_attributes": True}
