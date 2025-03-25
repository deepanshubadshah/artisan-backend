# app/models/lead.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Lead(Base):
    """
    SQLAlchemy model for the 'leads' table.
    """
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)  # Unique identifier for the lead
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)  # Email address (unique)
    company = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    stage = Column(String, default="New")
    engaged = Column(Boolean, default=False)
    last_contacted = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())