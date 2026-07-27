"""Asset management routes."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Asset, User
from app.schemas.assets import AssetListResponse, AssetResponse, AssetUpdateRequest, AssetUploadResponse

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=AssetListResponse)
def list_assets(
    asset_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List assets for current user."""
    query = db.query(Asset).filter(Asset.user_id == current_user.id)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    items = query.order_by(Asset.created_at.desc()).all()
    return AssetListResponse(
        items=[AssetResponse.model_validate(a) for a in items],
        total=len(items),
    )


@router.post("/upload", response_model=AssetUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile = File(...),
    asset_type: str = "image",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a media asset."""
    import uuid

    storage_key = f"uploads/{current_user.id}/{uuid.uuid4()}/{file.filename}"

    asset = Asset(
        user_id=current_user.id,
        asset_type=asset_type,
        storage_key=storage_key,
        original_filename=file.filename,
        file_size_bytes=0,  # Would be actual size after upload
        mime_type=file.content_type,
        provider="s3",
        is_public=False,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return AssetUploadResponse(
        id=asset.id,
        storage_key=asset.storage_key,
        url=f"https://assets.trendtube.ai/{storage_key}",
    )


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get asset details."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return AssetResponse.model_validate(asset)


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    payload: AssetUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update asset metadata."""
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == current_user.id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.user_id == current_user.id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    db.delete(asset)
    db.commit()

