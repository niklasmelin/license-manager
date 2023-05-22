"""License Server schemas for the License Manager API."""
from typing import Optional

from pydantic import BaseModel, PositiveInt

from lm_backend.api.schemas.base import BaseCreateSchema, BaseUpdateSchema
from lm_backend.constants import LicenseServerType


class LicenseServerCreateSchema(BaseCreateSchema):
    """
    License server to be created in the database.
    """

    config_id: int
    host: str
    port: PositiveInt
    type: LicenseServerType


class LicenseServerUpdateSchema(BaseUpdateSchema):
    """
    License server to be updated in the database.
    """

    config_id: Optional[int] = None
    host: Optional[str] = None
    port: Optional[PositiveInt] = None
    type: Optional[LicenseServerType] = None


class LicenseServerSchema(BaseModel):
    """
    License server response from the database.
    """

    id: int
    config_id: int
    host: str
    port: PositiveInt
    type: LicenseServerType

    class Config:
        orm_mode = True