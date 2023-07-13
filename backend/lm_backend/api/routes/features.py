from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from lm_backend.api.cruds.generic import GenericCRUD
from lm_backend.api.models.feature import Feature
from lm_backend.api.models.inventory import Inventory
from lm_backend.api.schemas.feature import FeatureCreateSchema, FeatureSchema, FeatureUpdateSchema
from lm_backend.api.schemas.inventory import InventoryCreateSchema, InventoryUpdateSchema
from lm_backend.database import SecureSession, secure_session
from lm_backend.permissions import Permissions

router = APIRouter()


crud_feature = GenericCRUD(Feature, FeatureCreateSchema, FeatureUpdateSchema)
crud_inventory = GenericCRUD(Inventory, InventoryCreateSchema, InventoryUpdateSchema)


@router.post(
    "/",
    response_model=FeatureSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_feature(
    feature: FeatureCreateSchema,
    secure_session: SecureSession = Depends(secure_session(Permissions.FEATURE_EDIT)),
):
    """Create a new feature and its inventory."""
    feature_created: Feature = await crud_feature.create(db_session=secure_session.session, obj=feature)
    inventory = InventoryCreateSchema(feature_id=feature_created.id, total=0, used=0)
    await crud_inventory.create(db_session=secure_session.session, obj=inventory)
    return await crud_feature.read(db_session=secure_session.session, id=feature_created.id)


@router.get(
    "/",
    response_model=List[FeatureSchema],
    status_code=status.HTTP_200_OK,
)
async def read_all_features(
    search: Optional[str] = Query(None),
    sort_field: Optional[str] = Query(None),
    sort_ascending: bool = Query(True),
    secure_session: SecureSession = Depends(secure_session(Permissions.FEATURE_VIEW)),
):
    """Return all features with associated bookings and inventory."""
    return await crud_feature.read_all(
        db_session=secure_session.session,
        search=search,
        sort_field=sort_field,
        sort_ascending=sort_ascending,
    )


@router.get(
    "/{feature_id}",
    response_model=FeatureSchema,
    status_code=status.HTTP_200_OK,
)
async def read_feature(
    feature_id: int,
    secure_session: SecureSession = Depends(secure_session(Permissions.FEATURE_VIEW)),
):
    """Return a feature with associated bookings and inventory with the given id."""
    return await crud_feature.read(db_session=secure_session.session, id=feature_id)


@router.put(
    "/{feature_id}",
    response_model=FeatureSchema,
    status_code=status.HTTP_200_OK,
)
async def update_feature(
    feature_id: int,
    feature_update: FeatureUpdateSchema,
    secure_session: SecureSession = Depends(secure_session(Permissions.FEATURE_EDIT)),
):
    """Update a feature in the database."""
    return await crud_feature.update(
        db_session=secure_session.session,
        id=feature_id,
        obj=feature_update,
    )


@router.put(
    "/{feature_id}/update_inventory",
    response_model=FeatureSchema,
    status_code=status.HTTP_200_OK,
)
async def update_inventory(
    feature_id: int,
    inventory_update: InventoryUpdateSchema,
    secure_session: SecureSession = Depends(secure_session(Permissions.FEATURE_EDIT)),
):
    """Update the inventory of a feature in the database."""
    inventory = await crud_inventory.filter(
        db_session=secure_session.session, filter_field=Inventory.feature_id, filter_term=feature_id
    )
    if inventory:
        await crud_inventory.update(
            db_session=secure_session.session,
            id=inventory.id,
            obj=inventory_update,
        )

    return await crud_feature.read(db_session=secure_session.session, id=feature_id)


@router.delete(
    "/{feature_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_feature(
    feature_id: int,
    secure_session: SecureSession = Depends(secure_session(Permissions.FEATURE_EDIT)),
):
    """
    Delete a feature from the database.

    This will also delete the inventory.
    """
    return await crud_feature.delete(db_session=secure_session.session, id=feature_id)
