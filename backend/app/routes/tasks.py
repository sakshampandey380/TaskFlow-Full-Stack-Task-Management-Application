from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.auth.deps import get_current_user
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskCompleteToggle
from backend.app.schemas.stats import TaskStatsOut
from backend.app.schemas.common import APIResponse
from backend.app.services.task_service import (
    get_user_tasks,
    get_task_by_id,
    create_task,
    update_task,
    toggle_task_complete,
    delete_task,
    get_task_stats
)
from backend.app.services.seed_service import seed_user_data
from backend.app.utils.response import success_response

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=APIResponse[List[TaskOut]])
def list_tasks(
    search: Optional[str] = Query(None, description="Search across title, description, category, and tags"),
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed, overdue"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, urgent"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_important: Optional[bool] = Query(None, description="Filter starred/important tasks"),
    due_filter: Optional[str] = Query(None, description="Quick due date filter: today, upcoming, overdue"),
    sort_by: Optional[str] = Query("newest", description="Sort by: newest, oldest, due_date, priority, recently_updated, title"),
    order: Optional[str] = Query("desc", description="Sort direction: asc or desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all tasks for the authenticated user matching filter, search, and sort criteria."""
    tasks = get_user_tasks(
        db=db,
        user_id=current_user.id,
        search=search,
        status_filter=status,
        priority=priority,
        category_id=category_id,
        is_important=is_important,
        due_filter=due_filter,
        sort_by=sort_by,
        order=order
    )
    task_outs = [TaskOut.model_validate(t) for t in tasks]
    return success_response(
        data=[t.model_dump() for t in task_outs],
        message=f"Retrieved {len(task_outs)} tasks successfully."
    )


@router.get("/stats", response_model=APIResponse[TaskStatsOut])
def get_dashboard_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate and return live task statistics, completion rates, and priority/category distributions."""
    stats = get_task_stats(db=db, user_id=current_user.id)
    return success_response(
        data=stats,
        message="Task statistics calculated successfully."
    )


@router.post("", response_model=APIResponse[TaskOut], status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task in MySQL database with tags and category."""
    task = create_task(db=db, user_id=current_user.id, task_data=task_in)
    return success_response(
        data=TaskOut.model_validate(task).model_dump(),
        message="Task created successfully.",
        status_code=status.HTTP_201_CREATED
    )


@router.get("/{task_id}", response_model=APIResponse[TaskOut])
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details of a single task by ID."""
    task = get_task_by_id(db=db, task_id=task_id, user_id=current_user.id)
    return success_response(
        data=TaskOut.model_validate(task).model_dump(),
        message="Task retrieved successfully."
    )


@router.put("/{task_id}", response_model=APIResponse[TaskOut])
def update_existing_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update title, description, priority, category, due dates, tags, and status."""
    task = update_task(db=db, task_id=task_id, user_id=current_user.id, task_data=task_in)
    return success_response(
        data=TaskOut.model_validate(task).model_dump(),
        message="Task updated successfully."
    )


@router.patch("/{task_id}/complete", response_model=APIResponse[TaskOut])
def toggle_completion(
    task_id: int,
    toggle_in: Optional[TaskCompleteToggle] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle or explicitly set the completed status of a task and update database timestamp."""
    explicit_state = toggle_in.completed if toggle_in is not None else None
    task = toggle_task_complete(db=db, task_id=task_id, user_id=current_user.id, explicit_state=explicit_state)
    state_str = "completed" if task.status == "completed" else "marked as incomplete"
    return success_response(
        data=TaskOut.model_validate(task).model_dump(),
        message=f"Task {state_str} successfully."
    )


@router.delete("/{task_id}", response_model=APIResponse[dict])
def remove_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently delete a task from MySQL database."""
    delete_task(db=db, task_id=task_id, user_id=current_user.id)
    return success_response(
        data={"deleted_task_id": task_id},
        message="Task permanently deleted successfully."
    )


@router.post("/seed-demo", response_model=APIResponse[dict])
def seed_demo_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Populate realistic sample tasks and categories for exploration and portfolio demonstration."""
    result = seed_user_data(db=db, user=current_user)
    return success_response(
        data=result,
        message=result["message"]
    )
