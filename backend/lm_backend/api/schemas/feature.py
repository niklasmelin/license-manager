"""Feature schemas for the License Manager API."""
from typing import Optional

from pydantic import BaseModel

from lm_backend.api.schemas.base import BaseCreateSchema, BaseUpdateSchema
from lm_backend.api.schemas.inventory import InventorySchema
from lm_backend.api.schemas.product import ProductSchema


class FeatureCreateSchema(BaseCreateSchema):
    """
    Represents the features in a feature configuration.
    """

    name: str
    product_id: int
    config_id: int
    reserved: int


class FeatureUpdateSchema(BaseUpdateSchema):
    """
    Represents the features in a feature configuration.
    """

    name: Optional[str] = None
    product_id: Optional[int] = None
    config_id: Optional[int] = None
    reserved: Optional[int] = None


class FeatureSchema(BaseModel):
    """
    Represents the features in a feature configuration.
    """

    id: int
    name: str
    product: ProductSchema
    config_id: int
    reserved: int
    inventory: Optional[InventorySchema] = None

    class Config:
        orm_mode = True
