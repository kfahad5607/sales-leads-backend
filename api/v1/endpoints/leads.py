from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, update, delete
from db.sql import get_session
from models.leads import Lead, LeadCreate, LeadUpdate

router = APIRouter()

@router.get("/")
async def get_leads(session: AsyncSession=Depends(get_session)):
    statement = select(Lead).order_by(Lead.created_at)
    result = await session.execute(statement)
    return result.scalars().all()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_lead(lead_create: LeadCreate, session: AsyncSession=Depends(get_session)):
    new_lead = Lead(**lead_create.model_dump())
    session.add(new_lead)
    await session.commit()
    return new_lead

@router.get("/{lead_id}")
async def get_lead(lead_id: UUID, session: AsyncSession=Depends(get_session)):
    statement = select(Lead).where(Lead.id == lead_id)
    result = await session.execute(statement)
    return result.scalars().first()

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")
        
        await session.commit()
        return updated_lead
    
    except IntegrityError as e:
        print(f"IntegrityError in update_lead {e=} {type(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lead with that email already exists.")

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: UUID,  session: AsyncSession=Depends(get_session)):
    statement = (
        delete(Lead)
        .where(Lead.id == lead_id)
        .returning(Lead)
    )
    result = await session.execute(statement)
    deleted_lead = result.scalars().first()

    if not deleted_lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found.")

    await session.commit()