from sqlalchemy import Column, Text, DateTime, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    firebase_uid = Column(Text, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    display_name = Column(Text)
    role = Column(Text, nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
