# app/crud/lead_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, asc, desc, or_
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate
from app.core.logger import logger
from uuid import UUID
import json
from datetime import datetime
from app.websockets import manager  # WebSocket manager


async def create_lead(db: AsyncSession, lead: LeadCreate, current_user: dict):
    """
    Create a new lead in the database and notify connected clients.
    """
    new_lead = Lead(**lead.model_dump())
    db.add(new_lead)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Error during commit in create_lead: {e}", exc_info=True)
        raise e
    await db.refresh(new_lead)

    created_lead_data = lead.model_dump()
    created_lead_data.pop("last_contacted", None)

    # Notify via WebSocket about the new lead
    new_lead_message = {
        "event": "lead_created",
        "lead_id": str(new_lead.id),
        "lead_data": created_lead_data,
        "source": current_user.get("id"),
        "sourceName": current_user.get("name"),
        "message": f"{current_user.get('name')} added a new lead: {new_lead.name}"
    }
    await manager.broadcast(json.dumps(new_lead_message))
    return new_lead


async def get_leads(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    filters: dict = None
):
    stmt = select(Lead)
    if search:
        stmt = stmt.filter(
            or_(
                Lead.name.ilike(f"%{search}%"),
                Lead.email.ilike(f"%{search}%"),
                Lead.company.ilike(f"%{search}%")
            )
        )
    if filters:
        if filters.get("stage"):
            stmt = stmt.filter(Lead.stage == filters["stage"])
        if filters.get("engaged"):
            engaged_value = filters["engaged"].lower() == "true"
            stmt = stmt.filter(Lead.engaged == engaged_value)
        if filters.get("createdAtStart"):
            try:
                start_date = datetime.strptime(filters["createdAtStart"], "%Y-%m-%d")
                stmt = stmt.filter(Lead.created_at >= start_date)
            except Exception as e:
                logger.info(f"Error parsing createdAtStart: {e}")
        if filters.get("createdAtEnd"):
            try:
                end_date = datetime.strptime(filters["createdAtEnd"], "%Y-%m-%d")
                stmt = stmt.filter(Lead.created_at <= end_date)
            except Exception as e:
                logger.error(f"Error parsing createdAtEnd: {e}")
        if filters.get("sortField"):
            sort_field = filters["sortField"]
            sort_order = filters.get("sortOrder", "desc")
            order_clause = asc(getattr(Lead, sort_field)) if sort_order.lower() == "asc" else desc(getattr(Lead, sort_field))
            stmt = stmt.order_by(order_clause)
        else:
            stmt = stmt.order_by(desc(Lead.created_at))
    else:
        stmt = stmt.order_by(desc(Lead.created_at))

    # Calculate total count using a subquery
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)
    leads = (await db.execute(stmt)).scalars().all()

    return {"items": leads, "total": total}



async def get_lead(db: AsyncSession, lead_id: UUID):
    """
    Retrieve a lead by ID.
    """
    stmt = select(Lead).filter(Lead.id == lead_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_lead(db: AsyncSession, lead_id: UUID, lead_update: LeadUpdate, current_user: dict):
    """
    Update an existing lead and notify connected clients.
    """
    db_lead = await get_lead(db, lead_id)
    if not db_lead:
        return None

    update_data = lead_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lead, key, value)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Error during commit in update_lead: {e}", exc_info=True)
        raise e
    await db.refresh(db_lead)

    update_data.pop("last_contacted", None)

    # Broadcast update event
    update_message = {
        "event": "lead_updated",
        "lead_id": str(lead_id),
        "updated_data": update_data,
        "source": current_user.get("id"),
        "sourceName": current_user.get("name"),
        "message": f"{current_user.get('name')} updated lead {db_lead.name}"
    }
    await manager.broadcast(json.dumps(update_message))
    return db_lead


async def delete_lead(db: AsyncSession, lead_id: UUID, current_user: dict):
    """
    Delete a lead and notify connected clients.
    """
    db_lead = await get_lead(db, lead_id)
    if not db_lead:
        return None

    await db.delete(db_lead)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Error during commit in delete_lead: {e}", exc_info=True)
        raise e

    # Broadcast delete event
    delete_message = {
        "event": "lead_deleted",
        "lead_id": str(lead_id),
        "source": current_user.get("id"),
        "sourceName": current_user.get("name"),
        "message": f"{current_user.get('name')} deleted lead {db_lead.name}"
    }
    await manager.broadcast(json.dumps(delete_message))
    return db_lead


async def get_all_leads(db: AsyncSession):
    """
    Retrieve all leads for CSV export.
    """
    stmt = select(Lead)
    result = await db.execute(stmt)
    return result.scalars().all()