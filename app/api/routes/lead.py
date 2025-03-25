# app/api/routes/lead.py
import csv
import io
import logging
import json
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Query, Depends, HTTPException, Response, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.dependencies import get_current_user
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.core.logger import logger
from app.services.lead_service import (
    add_lead_service,
    fetch_leads_service,
    fetch_lead_service,
    modify_lead_service,
    remove_lead_service,
    export_leads_service,
)

router = APIRouter()


@router.get("/export-leads", response_class=Response)
async def export_leads(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Export all leads as a CSV file.
    """
    try:
        logger.info("User requested lead export")
        leads = await export_leads_service(db)
        if not leads:
            logger.warning("No leads found to export")
        
        # Create an in-memory CSV file
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["ID", "Name", "Company", "Email", "Phone", "Stage", "Engaged", "Last Contacted", "Created At"])
        for lead in leads:
            writer.writerow([
                lead.id, lead.name, lead.company, lead.email,
                lead.phone, lead.stage, lead.engaged,
                lead.last_contacted, lead.created_at
            ])
        
        response = Response(content=stream.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=leads.csv"
        return response
    except Exception as e:
        logger.error(f"Error exporting leads: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to export leads")


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Create a new lead. Returns a 400 error if a lead with the given email already exists.
    """
    try:
        logger.info(f"User is creating a lead: {lead}")
        new_lead = await add_lead_service(db, lead, current_user)
        return new_lead
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Duplicate email error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Lead with this email already exists")
    except Exception as e:
        logger.error(f"Error creating lead: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error creating lead")


@router.get("/leads")
async def get_leads(
    skip: int = Query(0),
    limit: int = Query(10),
    search: Optional[str] = Query(None),
    filters: Optional[str] = Query(None),  # JSON string from query params
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db)
):
    try:
        filter_dict = json.loads(filters) if filters else {}
        logger.info(f"Decoded filters: {filter_dict}")
        logger.info(f"Fetching leads: skip={skip}, limit={limit}, search={search}, sort_by={sort_by}, sort_order={sort_order}")
        leads = await fetch_leads_service(db, skip, limit, search, sort_by, sort_order, filter_dict)
        return leads
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid filters format")
    except Exception as e:
        logger.error(f"Error fetching leads: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching leads")


@router.get("/id/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID = Path(..., title="Lead ID"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Retrieve a single lead by its ID.
    """
    try:
        logger.info(f"Fetching lead with ID {lead_id}")
        lead = await fetch_lead_service(db, lead_id)
        if not lead:
            logger.info(f"Lead with ID {lead_id} not found")
            return Response(status_code=404, content='{"detail": "Lead not found"}', media_type="application/json")
        return lead
    except Exception as e:
        logger.error(f"Error fetching lead ID {lead_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching lead")


@router.put("/id/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update an existing lead.
    """
    try:
        logger.info(f"User updating lead {lead_id} with data: {lead}")
        updated_lead = await modify_lead_service(db, lead_id, lead, current_user)
        if not updated_lead:
            logger.warning(f"Lead {lead_id} not found")
            raise HTTPException(status_code=404, detail="Lead not found")
        return updated_lead
    except Exception as e:
        logger.error(f"Error updating lead {lead_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update lead")


@router.delete("/id/{lead_id}")
async def delete_lead(
    lead_id: UUID = Path(..., title="Lead ID"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete a lead.
    """
    try:
        logger.info(f"User deleting lead {lead_id}")
        deleted_lead = await remove_lead_service(db, lead_id, current_user)
        if not deleted_lead:
            logger.info(f"Lead {lead_id} not found")
            return Response(status_code=404, content='{"detail": "Lead not found"}', media_type="application/json")
        return {"message": "Lead deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting lead {lead_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete lead")