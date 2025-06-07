from sqlmodel import SQLModel, Field 
from typing import Optional, List

class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str 
    image: str 
    description: str 
    creator: Optional[str]

class EventUpdate(SQLModel): 
    title: Optional[str] 
    image: Optional[str] 
    description: Optional[str] 
    tags: Optional[List[str]] 
    location: Optional[str]