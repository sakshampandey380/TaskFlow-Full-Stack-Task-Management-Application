from datetime import datetime, date, time, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, asc, func
from fastapi import HTTPException, status

from backend.app.models.task import Task
from backend.app.models.category import Category
from backend.app.models.tag import Tag, task_tags
from backend.app.schemas.task import TaskCreate, TaskUpdate


def _sync_task_tags(db: Session, user_id: int, task: Task, tag_names: List[str]):
    """Find or create tags for the user and associate them with the task."""
    cleaned_names = set(t.strip().lstrip("#").lower() for t in tag_names if t.strip())
    existing_tags = db.query(Tag).filter(Tag.user_id == user_id, Tag.name.in_(cleaned_names)).all() if cleaned_names else []
    existing_map = {t.name: t for t in existing_tags}

    final_tags = []
    for name in cleaned_names:
        if name in existing_map:
            final_tags.append(existing_map[name])
        else:
            new_tag = Tag(user_id=user_id, name=name)
            db.add(new_tag)
            db.flush()
            final_tags.append(new_tag)

    task.tags = final_tags


def get_user_tasks(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    category_id: Optional[int] = None,
    is_important: Optional[bool] = None,
    due_filter: Optional[str] = None,  # today, upcoming, overdue
    sort_by: Optional[str] = "newest",
    order: Optional[str] = "desc"
) -> List[Task]:
    """Retrieve filtered, searched, and sorted tasks for the specific user."""
    query = (
        db.query(Task)
        .options(joinedload(Task.category), joinedload(Task.tags))
        .filter(Task.user_id == user_id, Task.is_archived == 0)
    )

    today = date.today()

    # Search filter
    if search:
        search_term = f"%{search.strip()}%"
        # Match title, description, or category name, or associated tags
        tag_subquery = (
            db.query(task_tags.c.task_id)
            .join(Tag, Tag.id == task_tags.c.tag_id)
            .filter(Tag.name.ilike(search_term))
            .scalar_subquery()
        )
        query = query.outerjoin(Category, Task.category_id == Category.id).filter(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term),
                Category.name.ilike(search_term),
                Task.id.in_(tag_subquery)
            )
        )

    # Status filter
    if status_filter:
        sf = status_filter.lower().strip()
        if sf in ["pending", "in_progress", "completed"]:
            query = query.filter(Task.status == sf)
        elif sf == "overdue":
            query = query.filter(
                Task.status != "completed",
                Task.due_date < today
            )

    # Due date specific filter (Sidebar shortcuts: today, upcoming, completed)
    if due_filter:
        df = due_filter.lower().strip()
        if df == "today":
            query = query.filter(Task.due_date == today)
        elif df == "upcoming":
            query = query.filter(Task.due_date > today)
        elif df == "overdue":
            query = query.filter(
                Task.status != "completed",
                Task.due_date < today
            )

    # Priority filter
    if priority and priority.lower() in ["low", "medium", "high", "urgent"]:
        query = query.filter(Task.priority == priority.lower())

    # Category filter
    if category_id:
        query = query.filter(Task.category_id == category_id)

    # Important filter
    if is_important is not None:
        query = query.filter(Task.is_important == (1 if is_important else 0))

    # Sorting logic
    sort_by_lower = (sort_by or "newest").lower()
    is_desc = (order or "desc").lower() == "desc"

    if sort_by_lower == "newest":
        query = query.order_by(desc(Task.created_at) if is_desc else asc(Task.created_at))
    elif sort_by_lower == "oldest":
        query = query.order_by(asc(Task.created_at) if is_desc else desc(Task.created_at))
    elif sort_by_lower == "due_date":
        # Put null due dates at the end
        if is_desc:
            query = query.order_by(Task.due_date.is_(None), desc(Task.due_date), desc(Task.due_time))
        else:
            query = query.order_by(Task.due_date.is_(None), asc(Task.due_date), asc(Task.due_time))
    elif sort_by_lower == "priority":
        # Order by priority weight: urgent (4) -> high (3) -> medium (2) -> low (1)
        priority_case = func.field(Task.priority, "low", "medium", "high", "urgent")
        query = query.order_by(desc(priority_case) if is_desc else asc(priority_case))
    elif sort_by_lower == "recently_updated":
        query = query.order_by(desc(Task.updated_at) if is_desc else asc(Task.updated_at))
    elif sort_by_lower == "title":
        query = query.order_by(desc(Task.title) if is_desc else asc(Task.title))
    else:
        query = query.order_by(desc(Task.created_at))

    return query.all()


def get_task_by_id(db: Session, task_id: int, user_id: int) -> Task:
    """Fetch single task owned by user, or raise 404."""
    task = (
        db.query(Task)
        .options(joinedload(Task.category), joinedload(Task.tags))
        .filter(Task.id == task_id, Task.user_id == user_id, Task.is_archived == 0)
        .first()
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or access denied.")
    return task


def create_task(db: Session, user_id: int, task_data: TaskCreate) -> Task:
    """Create a new task with validated category and tag associations."""
    # Verify category ownership if provided
    if task_data.category_id:
        category = db.query(Category).filter(Category.id == task_data.category_id, Category.user_id == user_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected category does not exist.")

    completed_at = datetime.utcnow() if task_data.status == "completed" else None

    task = Task(
        user_id=user_id,
        category_id=task_data.category_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        due_time=task_data.due_time,
        is_important=1 if task_data.is_important else 0,
        completed_at=completed_at
    )
    db.add(task)
    db.flush()

    if task_data.tags:
        _sync_task_tags(db, user_id, task, task_data.tags)

    db.commit()
    db.refresh(task)
    return get_task_by_id(db, task.id, user_id)


def update_task(db: Session, task_id: int, user_id: int, task_data: TaskUpdate) -> Task:
    """Update task fields, validate relationships, and sync tags."""
    task = get_task_by_id(db, task_id, user_id)

    if task_data.category_id is not None:
        if task_data.category_id > 0:
            category = db.query(Category).filter(Category.id == task_data.category_id, Category.user_id == user_id).first()
            if not category:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected category does not exist.")
            task.category_id = task_data.category_id
        else:
            task.category_id = None

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.due_time is not None:
        task.due_time = task_data.due_time
    if task_data.is_important is not None:
        task.is_important = 1 if task_data.is_important else 0
    if task_data.is_archived is not None:
        task.is_archived = 1 if task_data.is_archived else 0
    if task_data.sort_order is not None:
        task.sort_order = task_data.sort_order

    if task_data.status is not None:
        prev_status = task.status
        task.status = task_data.status
        if task_data.status == "completed" and prev_status != "completed":
            task.completed_at = datetime.utcnow()
        elif task_data.status != "completed":
            task.completed_at = None

    if task_data.tags is not None:
        _sync_task_tags(db, user_id, task, task_data.tags)

    db.commit()
    db.refresh(task)
    return get_task_by_id(db, task.id, user_id)


def toggle_task_complete(db: Session, task_id: int, user_id: int, explicit_state: Optional[bool] = None) -> Task:
    """Toggle task completion state and update completed_at timestamp in database."""
    task = get_task_by_id(db, task_id, user_id)

    if explicit_state is not None:
        new_status = "completed" if explicit_state else "pending"
    else:
        new_status = "pending" if task.status == "completed" else "completed"

    task.status = new_status
    if new_status == "completed":
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None

    db.commit()
    db.refresh(task)
    return get_task_by_id(db, task.id, user_id)


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """Permanently delete a task belonging to user."""
    task = get_task_by_id(db, task_id, user_id)
    db.delete(task)
    db.commit()
    return True


def get_task_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Calculate comprehensive task statistics, priority distribution, category breakdown, and completion rate."""
    today = date.today()
    tasks = db.query(Task).filter(Task.user_id == user_id, Task.is_archived == 0).all()

    total = len(tasks)
    completed = 0
    pending = 0
    in_progress = 0
    overdue = 0
    important = 0
    today_count = 0
    upcoming = 0

    priority_counts = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
    category_counts_map: Dict[int, int] = {}

    for t in tasks:
        if t.status == "completed":
            completed += 1
        elif t.status == "in_progress":
            in_progress += 1
        else:
            pending += 1

        # Overdue check: past due date and not completed
        if t.status != "completed" and t.due_date and t.due_date < today:
            overdue += 1

        if t.is_important:
            important += 1

        if t.due_date:
            if t.due_date == today:
                today_count += 1
            elif t.due_date > today:
                upcoming += 1

        if t.priority in priority_counts:
            priority_counts[t.priority] += 1

        if t.category_id:
            category_counts_map[t.category_id] = category_counts_map.get(t.category_id, 0) + 1

    completion_rate = round((completed / total * 100), 1) if total > 0 else 0.0

    # Fetch user categories for breakdown
    categories = db.query(Category).filter(Category.user_id == user_id).all()
    by_category = [
        {
            "id": cat.id,
            "name": cat.name,
            "color": cat.color or "#4F46E5",
            "count": category_counts_map.get(cat.id, 0)
        }
        for cat in categories
    ]

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "in_progress_tasks": in_progress,
        "overdue_tasks": overdue,
        "important_tasks": important,
        "today_tasks": today_count,
        "upcoming_tasks": upcoming,
        "completion_rate": completion_rate,
        "by_priority": priority_counts,
        "by_category": by_category
    }
