# app/schemas/lead.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional

class LeadBase(BaseModel):
    """
    Base schema for a lead.
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    stage: Optional[str] = None           # Named stage, e.g., "New", "Qualified", etc.
    engaged: Optional[bool] = None

    last_contacted: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LeadCreate(LeadBase):
    """
    Schema for creating a new lead.
    """
    pass

class LeadUpdate(BaseModel):
    """
    Schema for updating an existing lead.
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    stage: Optional[str] = None
    engaged: Optional[bool] = None
    last_contacted: Optional[datetime] = None

class LeadResponse(LeadBase):
    """
    Schema for returning lead data in responses.
    """
    id: UUID

    class Config:
        from_attributes = True  # Convert attribute names to snake_case for JSON responses