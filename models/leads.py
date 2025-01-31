from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Column, DateTime
from pydantic import EmailStr

def get_current_timestamp():
    return datetime.now(timezone.utc) 

class LeadBase(SQLModel):
    name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255, unique=True)
    company_name: str = Field(max_length=255)
    engaged: bool = Field(default=False)
    last_contacted_at: Optional[datetime] = Field(default=None, sa_column=Column(
        DateTime(timezone=True)
    ))

class Lead(LeadBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=get_current_timestamp, sa_column=Column(
        DateTime(timezone=True),
        nullable=False
    ))
    updated_at: datetime = Field(default_factory=get_current_timestamp, sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=get_current_timestamp
    ))

class LeadPublic(Lead, table=False):
    pass

class LeadCreate(LeadBase):
    pass