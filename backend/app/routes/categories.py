from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.models.task import Task
from backend.app.auth.deps import get_current_user
from backend.app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from backend.app.schemas.common import APIResponse
from backend.app.utils.response import success_response

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=APIResponse[List[CategoryOut]])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all categories for user with task counts."""
    categories = db.query(Category).filter(Category.user_id == current_user.id).order_by(Category.name.asc()).all()

    # Calculate task counts
    counts = (
        db.query(Task.category_id, func.count(Task.id))
        .filter(Task.user_id == current_user.id, Task.is_archived == 0)
        .group_by(Task.category_id)
        .all()
    )
    counts_map = {cat_id: count for cat_id, count in counts if cat_id is not None}

    cat_outs = []
    for c in categories:
        out = CategoryOut.model_validate(c)
        out.task_count = counts_map.get(c.id, 0)
        cat_outs.append(out)

    return success_response(
        data=[c.model_dump() for c in cat_outs],
        message=f"Retrieved {len(cat_outs)} categories."
    )


@router.post("", response_model=APIResponse[CategoryOut], status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category for user with custom color and icon."""
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == cat_in.name.strip()
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{cat_in.name.strip()}' already exists."
        )

    cat = Category(
        user_id=current_user.id,
        name=cat_in.name.strip(),
        description=cat_in.description,
        icon=cat_in.icon or "folder",
        color=cat_in.color or "#4F46E5"
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)

    out = CategoryOut.model_validate(cat)
    out.task_count = 0
    return success_response(
        data=out.model_dump(),
        message="Category created successfully.",
        status_code=status.HTTP_201_CREATED
    )


@router.put("/{category_id}", response_model=APIResponse[CategoryOut])
def update_category(
    category_id: int,
    cat_in: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update existing category details."""
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    if cat_in.name is not None and cat_in.name.strip() != cat.name:
        existing = db.query(Category).filter(
            Category.user_id == current_user.id,
            Category.name == cat_in.name.strip()
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{cat_in.name.strip()}' already exists."
            )
        cat.name = cat_in.name.strip()

    if cat_in.description is not None:
        cat.description = cat_in.description
    if cat_in.icon is not None:
        cat.icon = cat_in.icon
    if cat_in.color is not None:
        cat.color = cat_in.color

    db.commit()
    db.refresh(cat)

    task_count = db.query(Task).filter(Task.category_id == cat.id, Task.is_archived == 0).count()
    out = CategoryOut.model_validate(cat)
    out.task_count = task_count

    return success_response(
        data=out.model_dump(),
        message="Category updated successfully."
    )


@router.delete("/{category_id}", response_model=APIResponse[dict])
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a category. Associated tasks will have their category unset to uncategorized."""
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    db.delete(cat)
    db.commit()

    return success_response(
        data={"deleted_category_id": category_id},
        message="Category deleted successfully."
    )
