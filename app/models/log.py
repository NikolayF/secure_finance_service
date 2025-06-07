from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from uuid import UUID

def get_utc_timestamp():
    return datetime.now()

class Log(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=get_utc_timestamp)
    user_id: int = Field(foreign_key="user.id")
    model_request_id: Optional[UUID] = Field(default=None, index=True)
    event_type: str
    description: str
    user: Optional["User"] = Relationship(back_populates="logs")

    