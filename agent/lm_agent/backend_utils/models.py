from typing import List

from pydantic import BaseModel, Field, PositiveInt

from lm_agent.backend_utils.constants import LicenseServerType
from lm_agent.config import PRODUCT_FEATURE_RX


class LicenseServerSchema(BaseModel):
    """
    License server response from the database.
    """

    id: int
    config_id: int
    host: str
    port: PositiveInt


class ProductSchema(BaseModel):
    """
    Represents a feature's product.
    """

    id: int
    name: str


class InventorySchema(BaseModel):
    """
    Represents the inventory of a feature.
    """

    id: int
    feature_id: int
    total: int
    used: int


class FeatureSchema(BaseModel):
    """
    Represents the features in a feature configuration.
    """

    id: int
    name: str
    product: ProductSchema
    config_id: int
    reserved: int
    inventory: InventorySchema


class ConfigurationSchema(BaseModel):
    """
    Represents the configuration for a set of features.
    """

    id: int
    name: str
    cluster_id: int
    features: List[FeatureSchema] = []
    license_servers: List[LicenseServerSchema] = []
    grace_time: int
    type: LicenseServerType


class BookingSchema(BaseModel):
    """
    Represents the booking of a feature.
    """

    id: int
    job_id: int
    feature_id: int
    quantity: int


class JobSchema(BaseModel):
    """
    Represents the jobs submitted in a cluster.
    """

    id: int
    slurm_job_id: str
    cluster_id: int
    username: str
    lead_host: str

    bookings: List[BookingSchema] = []


class ClusterSchema(BaseModel):
    """
    Cluster response from the database.
    """

    id: int
    name: str
    client_id: str
    configurations: List[ConfigurationSchema] = []
    jobs: List[JobSchema] = []


class LicenseBooking(BaseModel):
    """
    Structure to represent a license booking.
    """

    product_feature: str = Field(..., regex=PRODUCT_FEATURE_RX)
    quantity: int


class LicenseBookingRequest(BaseModel):
    """
    Structure to represent a list of license bookings.
    """

    slurm_job_id: int
    user_name: str
    lead_host: str
    bookings: List[LicenseBooking] = []