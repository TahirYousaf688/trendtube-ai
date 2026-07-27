"""Channel management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Channel, ChannelPlaylist, User
from app.schemas.channels import (
    ChannelCreateRequest,
    ChannelListResponse,
    ChannelResponse,
    ChannelUpdateRequest,
    PlaylistCreateRequest,
    PlaylistResponse,
)

router = APIRouter(prefix="/channels", tags=["Channels"])


@router.get("", response_model=ChannelListResponse)
def list_channels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all channels for the current user."""
    channels = db.query(Channel).filter(Channel.owner_id == current_user.id).all()
    return ChannelListResponse(
        items=[ChannelResponse.model_validate(c) for c in channels],
        total=len(channels),
    )


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
def create_channel(
    payload: ChannelCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new YouTube channel."""
    channel = Channel(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        youtube_channel_id=payload.youtube_channel_id,
        youtube_handle=payload.youtube_handle,
        settings=payload.settings or {},
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return ChannelResponse.model_validate(channel)


@router.get("/{channel_id}", response_model=ChannelResponse)
def get_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get channel details."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.owner_id == current_user.id,
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return ChannelResponse.model_validate(channel)


@router.put("/{channel_id}", response_model=ChannelResponse)
def update_channel(
    channel_id: int,
    payload: ChannelUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update channel settings."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.owner_id == current_user.id,
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)
    db.commit()
    db.refresh(channel)
    return ChannelResponse.model_validate(channel)


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a channel."""
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.owner_id == current_user.id,
    ).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    db.delete(channel)
    db.commit()


@router.get("/{channel_id}/playlists", response_model=list[PlaylistResponse])
def list_playlists(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List playlists for a channel."""
    playlists = db.query(ChannelPlaylist).filter(ChannelPlaylist.channel_id == channel_id).all()
    return [PlaylistResponse.model_validate(p) for p in playlists]


@router.post("/{channel_id}/playlists", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
def create_playlist(
    channel_id: int,
    payload: PlaylistCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new playlist."""
    playlist = ChannelPlaylist(
        channel_id=channel_id,
        title=payload.title,
        description=payload.description,
        is_public=payload.is_public,
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return PlaylistResponse.model_validate(playlist)

