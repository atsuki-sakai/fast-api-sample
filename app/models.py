from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: str
    class Config:
        schema_extra = {
            "example": {
                "name": "Sample Item",
                "description": "A sample item description"
            }
        }

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
