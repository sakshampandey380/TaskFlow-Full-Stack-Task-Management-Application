from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.tag import Tag
from backend.app.auth.deps import get_current_user
from backend.app.schemas.tag import TagCreate, TagOut
from backend.app.schemas.common import APIResponse
from backend.app.utils.response import success_response

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=APIResponse[List[TagOut]])
def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all user tags."""
    tags = db.query(Tag).filter(Tag.user_id == current_user.id).order_by(Tag.name.asc()).all()
    return success_response(
        data=[TagOut.model_validate(t).model_dump() for t in tags],
        message=f"Retrieved {len(tags)} tags."
    )


@router.post("", response_model=APIResponse[TagOut], status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_in: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new tag for user."""
    cleaned_name = tag_in.name.strip().lstrip("#").lower()
    existing = db.query(Tag).filter(Tag.user_id == current_user.id, Tag.name == cleaned_name).first()
    if existing:
        return success_response(
            data=TagOut.model_validate(existing).model_dump(),
            message="Tag already exists."
        )

    tag = Tag(user_id=current_user.id, name=cleaned_name)
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return success_response(
        data=TagOut.model_validate(tag).model_dump(),
        message="Tag created successfully.",
        status_code=status.HTTP_201_CREATED
    )


@router.delete("/{tag_id}", response_model=APIResponse[dict])
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a tag."""
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == current_user.id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")

    db.delete(tag)
    db.commit()
    return success_response(
        data={"deleted_tag_id": tag_id},
        message="Tag deleted successfully."
    )
