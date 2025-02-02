from enum import Enum
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Column, Computed, DateTime, Enum as SQLAlchemyEnum, BigInteger, Field, func
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from pydantic import EmailStr
from utils.helpers import get_current_timestamp

class LeadStage(str, Enum):
    LOST = "lost"
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"

class LeadBase(SQLModel):
    name: str = Field(max_length=150)
    email: EmailStr = Field(max_length=150, unique=True)
    company_name: str = Field(max_length=150)
    is_engaged: bool = Field(default=False)
    stage: LeadStage = Field(sa_column=Column(SQLAlchemyEnum(LeadStage)), default=LeadStage.NEW)
    last_contacted_at: Optional[datetime] = Field(default=None, sa_column=Column(
        DateTime(timezone=True)
    ))

class Lead(LeadBase, table=True):
    id: int = Field(default=None, sa_column=Column(BigInteger, autoincrement=True, primary_key=True))
    created_at: datetime = Field(default_factory=get_current_timestamp, sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    ))
    updated_at: datetime = Field(default_factory=get_current_timestamp, sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=func.now()
    ))

    search_vector: str = Field(
        sa_column=Column(
            TSVECTOR,
            Computed(
                "to_tsvector('english', name || ' ' || email || ' ' || company_name)",
                persisted=True
            )
        )
    )

    __table_args__ = (
        Index("idx_lead_search", "search_vector", postgresql_using="gin"),
    )

class LeadPublic(LeadBase):
    id: int = Lead.id

class LeadCreate(LeadBase):
    pass

class LeadUpdate(LeadBase):
    pass

class BulkLeadRequest(SQLModel):
    ids: List[int]

lead_public_fields = [
    Lead.id,
    Lead.name, 
    Lead.email, 
    Lead.company_name, 
    Lead.stage, 
    Lead.is_engaged, 
    Lead.last_contacted_at
]