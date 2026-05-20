from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey, func
from app.database import Base


class RequestLog(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, ForeignKey("users.firebase_uid"), nullable=False)
    image_filename = Column(Text)
    predicted_class = Column(Text)
    confidence = Column(Float)
    latency_ms = Column(Integer)
    ram_mb = Column(Float)
    cpu_percent = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
