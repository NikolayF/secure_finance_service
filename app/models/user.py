from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    password: str
    events: Optional[str]
    balance: Optional["Balance"] = Relationship(back_populates="user")
    logs: List["Log"] = Relationship(back_populates="user")
    is_superuser: bool = Field(default=False)
    