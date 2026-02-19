"""
Shared Pydantic base config and common field types.
All schemas use `from_attributes = True` to work with SQLAlchemy ORM objects.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AppModel(BaseModel):
    """Base for all response schemas — enables ORM mode."""
    model_config = ConfigDict(from_attributes=True)


class UUIDModel(AppModel):
    id: uuid.UUID


class TimestampedModel(UUIDModel):
    created_at: datetime
