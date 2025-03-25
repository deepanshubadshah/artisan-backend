# app/services/lead_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.crud.lead_crud import (
    create_lead,
    get_leads,
    get_lead,
    update_lead,
    delete_lead,
    get_all_leads
)
from app.schemas.lead import LeadCreate, LeadUpdate


async def export_leads_service(db: AsyncSession):
    """
    Retrieve all leads for CSV export.
    """
    return await get_all_leads(db)


async def add_lead_service(db: AsyncSession, lead_data: LeadCreate, current_user: dict):
    """
    Add a new lead.
    """
    return await create_lead(db, lead_data, current_user)


async def fetch_leads_service(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    filters: dict = None
):
    """
    Retrieve leads with pagination, filtering, and sorting.
    """
    return await get_leads(db, skip, limit, search, sort_by, sort_order, filters)


async def fetch_lead_service(db: AsyncSession, lead_id: UUID):
    """
    Retrieve a single lead.
    """
    return await get_lead(db, lead_id)


async def modify_lead_service(db: AsyncSession, lead_id: UUID, lead_data: LeadUpdate, current_user: dict):
    """
    Update an existing lead.
    """
    return await update_lead(db, lead_id, lead_data, current_user)

async def remove_lead_service(db: AsyncSession, lead_id: UUID, current_user: dict):
    """
    Delete a lead.
    """
    return await delete_lead(db, lead_id, current_user)