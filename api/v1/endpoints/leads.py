import csv
from io import StringIO
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc
from sqlmodel import select, update, delete, func, text
from db.sql import get_session
from models.leads import BulkLeadRequest, Lead, LeadCreate, LeadUpdate, lead_public_fields
from sqlalchemy.exc import IntegrityError
from utils.exceptions import BaseAppException, ResourceNotFoundException, ValidationException
from utils.logger import logger
from utils.helpers import get_total_pages

router = APIRouter()

def prepare_leads_csv(leads: List[Lead]) -> StringIO:
    """Generate a CSV file from the list of leads."""
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(['ID', 'Name', 'Email', 'Company', 'Stage', 'Engaged', 'Last Contacted'])

    for lead in leads:
        writer.writerow([lead.id, lead.name, lead.email, lead.company_name, lead.stage, lead.is_engaged, lead.last_contacted_at])
    
    csv_file.seek(0)

    return csv_file

def build_sorting_expression(sort_by: Optional[str], model: Lead) -> List:
    """Helper to handle sorting logic."""
    sort_expressions = []
    if sort_by:
        sort_fields = sort_by.split(",")

        for field in sort_fields:
            desc_order = field.startswith("-")
            col_name = field.lstrip("-")

            if not hasattr(model, col_name):
                raise ValidationException(message=f"Invalid sort field: {col_name}")

            sort_expr = desc(getattr(model, col_name)) if desc_order else asc(getattr(model, col_name))
            sort_expressions.append(sort_expr)

        sort_expressions.append(desc(model.created_at))

    return sort_expressions

def build_query_filter(query: str, model: Lead) -> Optional[str]:
    """Helper to handle query-based filtering logic."""
    where_clause = model.search_vector.op('@@')(text("plainto_tsquery('english', :query)"))
    return where_clause

@router.get("/")
async def get_leads(
    session: AsyncSession=Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=101),
    query: Optional[str] = Query(default=""),
    sort_by: Optional[str] = Query(None)
):
    try:
        query = query.strip()
        offset = (page - 1) * page_size
        stmt = select(*lead_public_fields)
        total_count_stmt = select(func.count()).select_from(Lead)

        if query:
            where_clause = build_query_filter(query, Lead)
            stmt = stmt.where(where_clause).params(query=query)
            total_count_stmt = total_count_stmt.where(where_clause).params(query=query)

        sort_expressions = build_sorting_expression(sort_by=sort_by, model=Lead)
        stmt = stmt.order_by(*sort_expressions).limit(page_size).offset(offset)

        results = await session.execute(stmt)

        # Get Total Leads
        total_results = await session.execute(total_count_stmt)
        total_count = total_results.scalar()

        leads = results.mappings().all()

        return {
            'current_page': page,
            'page_size': page_size,
            'total_records': total_count,
            'total_pages': get_total_pages(total_count, page_size),
            'data': leads
        }
    except ValidationException as e:
        raise
    except Exception as e:
        logger.error(f"Exception in get_leads ==> {e}")
        raise BaseAppException("Could not get the leads. Please try again later.") from e

@router.get("/export")
async def export_leads(
    session: AsyncSession=Depends(get_session),
    query: Optional[str] = Query(default=""),
    sort_by: Optional[str] = Query(None)
):
    try:
        query = query.strip()
        stmt = select(*lead_public_fields)
        CSV_ROW_LIMIT = 10000

        if query:
            where_clause = build_query_filter(query, Lead)
            stmt = stmt.where(where_clause).params(query=query)

        sort_expressions = build_sorting_expression(sort_by, Lead)
        stmt = stmt.order_by(*sort_expressions).limit(CSV_ROW_LIMIT)

        result = await session.execute(stmt)
        
        leads = result.mappings().all()
        csv_file = prepare_leads_csv(leads)

        return StreamingResponse(csv_file, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sales_leads.csv"})
    except ValidationException as e:
        raise
    except Exception as e:
        logger.error(f"Exception in get_leads ==> {e}")
        raise BaseAppException("Could not export the leads. Please try again later.") from e

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_lead(lead_create: LeadCreate, session: AsyncSession=Depends(get_session)):
    try:
        lead_create.name = lead_create.name.strip()
        lead_create.company_name = lead_create.company_name.strip()
        lead_create.email = lead_create.email.strip().lower()

        new_lead = Lead(**lead_create.model_dump())
        session.add(new_lead)
        await session.commit()

        new_lead_data = {field.name: getattr(new_lead, field.name) for field in lead_public_fields}

        return new_lead_data
    except IntegrityError as e:
        logger.error(f"IntegrityError in create_lead ==> {e}")
        raise ValidationException(status_code=status.HTTP_409_CONFLICT, message="Lead with that email already exists.")
    except Exception as e:
        logger.error(f"Exception in create_lead ==> {e}")
        await session.rollback()
        raise BaseAppException("Could not create the lead. Please try again later.") from e
   
@router.get("/{lead_id}")
async def get_lead(lead_id: int, session: AsyncSession=Depends(get_session)):
    try:
        stmt = select(Lead).where(Lead.id == lead_id)
        result = await session.execute(stmt)
        lead = result.scalars().first()
        
        if not lead:
            raise ResourceNotFoundException(message="Lead not found.")

        return lead
    except ResourceNotFoundException as e:
        raise
    except Exception as e:
        raise BaseAppException("Could not get the lead. Please try again later.") from e

@router.put("/{lead_id}")
async def update_lead(lead_id: int, lead_update: LeadUpdate,  session: AsyncSession=Depends(get_session)):
    try:
        stmt = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(
                name=lead_update.name.strip(),
                email=lead_update.email.strip().lower(),
                company_name=lead_update.company_name.strip(),
                is_engaged=lead_update.is_engaged,
                last_contacted_at=lead_update.last_contacted_at,
            )
            .returning(*lead_public_fields)
        )
        results = await session.execute(stmt)
        updated_lead = results.mappings().one_or_none()

        if not updated_lead:
            raise ResourceNotFoundException(message="Lead not found.")
        
        await session.commit()
        return updated_lead
    except ResourceNotFoundException as e:
        raise
    except IntegrityError as e:
        logger.error(f"IntegrityError in update_lead ==> {e}")
        raise ValidationException(status_code=status.HTTP_409_CONFLICT, message="Lead with that email already exists.")
    except Exception as e:
        await session.rollback()
        raise BaseAppException("Could not update the lead. Please try again later.") from e

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: int,  session: AsyncSession=Depends(get_session)):
    try:
        stmt = (
            delete(Lead)
            .where(Lead.id == lead_id)
            .returning(Lead.id)
        )
        result = await session.execute(stmt)
        deleted_lead = result.mappings().one_or_none()
    
        if not deleted_lead:
            raise ResourceNotFoundException(message="Lead not found.")

        await session.commit()
    except ResourceNotFoundException as e:
        raise
    except Exception as e:
        raise BaseAppException("Could not delete the lead. Please try again later.") from e
    
@router.post("/bulk-delete", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_leads(request: BulkLeadRequest, session: AsyncSession=Depends(get_session)):
    try:
        ids_to_delete = request.ids
        if not ids_to_delete:
            raise ValidationException(message="No IDs provided for deletion.")
        
        stmt = (
            delete(Lead)
            .where(Lead.id.in_(ids_to_delete))
        )
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Exception in bulk_delete_leads ==> {e}")
        await session.rollback()
        raise BaseAppException("Could not delete the leads. Please try again later.") from e