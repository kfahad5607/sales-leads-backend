from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db.sql import get_session
from models.leads import LeadCreate, Lead

router = APIRouter()

@router.get("/")
async def get_leads(session: AsyncSession=Depends(get_session)):
    statement = select(Lead).order_by(Lead.created_at)
    result = await session.execute(statement)
    return result.scalars().all()

@router.post("/")
async def create_lead(lead: LeadCreate, session: AsyncSession=Depends(get_session)):
    new_lead = Lead(**lead.model_dump())
    session.add(new_lead)
    await session.commit()
    return new_lead