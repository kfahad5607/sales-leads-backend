from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc
from sqlmodel import select, update, delete, func
from db.sql import get_session
from models.leads import Lead, LeadCreate, LeadUpdate
from sqlalchemy.exc import IntegrityError
from utils.exceptions import BaseAppException, ResourceNotFoundException, ValidationException
from utils.logger import logger
from utils.helpers import get_total_pages

router = APIRouter()

@router.get("/")
async def get_leads(
    session: AsyncSession=Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=101),
    sort: Optional[str] = Query(None)
):
    try:
        offset = (page - 1) * page_size
        stmt = select(Lead)

        sort_expressions = []
        if sort:
            sort_fields = sort.split(",")
            for field in sort_fields:
                desc_order = field.startswith("-")
                col_name = field.lstrip("-")

                if not hasattr(Lead, col_name):
                    raise ValidationException(message=f"Invalid sort field: {col_name}")

                sort_expr = desc(getattr(Lead, col_name)) if desc_order else asc(getattr(Lead, col_name))
                sort_expressions.append(sort_expr)

            sort_expressions.append(desc(Lead.created_at))
            stmt = stmt.order_by(*sort_expressions)

        stmt = stmt.limit(page_size).offset(offset)
        result = await session.execute(stmt)

        # Get Total Leads
        total_stmt = select(func.count()).select_from(Lead)
        total_results = await session.execute(total_stmt)
        total_count = total_results.scalar()

        return {
            'current_page': page,
            'page_size': page_size,
            'total_records': total_count,
            'total_pages': get_total_pages(total_count, page_size),
            'data': result.scalars().all()
        }
    except ValidationException as e:
        raise
    except Exception as e:
        logger.error(f"Exception in get_leads ==> {e}")
        raise BaseAppException("Could not get the leads. Please try again later.") from e

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_lead(lead_create: LeadCreate, session: AsyncSession=Depends(get_session)):
    try:
        new_lead = Lead(**lead_create.model_dump())
        session.add(new_lead)
        await session.commit()
        return new_lead
    except IntegrityError as e:
        logger.error(f"IntegrityError in create_lead ==> {e}")
        raise ValidationException(status_code=status.HTTP_409_CONFLICT, message="Lead with that email already exists.")
    except Exception as e:
        logger.error(f"Exception in create_lead ==> {e}")
        await session.rollback()
        raise BaseAppException("Could not create the lead. Please try again later.") from e
    

@router.get("/{lead_id}")
async def get_lead(lead_id: UUID, session: AsyncSession=Depends(get_session)):
    try:
        statement = select(Lead).where(Lead.id == lead_id)
        result = await session.execute(statement)
        lead = result.scalars().first()
        
        if not lead:
            raise ResourceNotFoundException(message="Lead not found.")

        return lead
    except ResourceNotFoundException as e:
        raise
    except Exception as e:
        raise BaseAppException("Could not get the lead. Please try again later.") from e

@router.put("/{lead_id}")
async def update_lead(lead_id: UUID, lead_update: LeadUpdate,  session: AsyncSession=Depends(get_session)):
    try:
        statement = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(
                name=lead_update.name,
                email=lead_update.email,
                company_name=lead_update.company_name,
                engaged=lead_update.engaged,
                last_contacted_at=lead_update.last_contacted_at,
            )
            .returning(Lead)
        )
        result = await session.execute(statement)
        updated_lead = result.scalars().first()

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
async def delete_lead(lead_id: UUID,  session: AsyncSession=Depends(get_session)):
    try:
        statement = (
            delete(Lead)
            .where(Lead.id == lead_id)
            .returning(Lead)
        )
        result = await session.execute(statement)
        deleted_lead = result.scalars().first()
    
        if not deleted_lead:
            raise ResourceNotFoundException(message="Lead not found.")

        await session.commit()
    except ResourceNotFoundException as e:
        raise
    except Exception as e:
        raise BaseAppException("Could not delete the lead. Please try again later.") from e