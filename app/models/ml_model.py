from sqlmodel import SQLModel, Field
from typing import Optional

class MlModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    version: float
    description: Optional[str]
    prediction_data: Optional[str]