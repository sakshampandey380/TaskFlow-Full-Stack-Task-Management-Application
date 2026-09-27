from datetime import date, datetime, timedelta, time
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.models.settings import UserSettings
from backend.app.schemas.task import TaskCreate
from backend.app.services.task_service import create_task


def seed_user_data(db: Session, user: User) -> dict:
    """Create default categories, settings, and realistic demo tasks for the user."""
    # Ensure default settings exist
    if not user.settings:
        settings = UserSettings(
            user_id=user.id,
            theme="light",
            default_task_priority="medium",
            default_task_status="pending",
            tasks_per_page=20,
            show_completed_tasks=1,
            email_notifications=1,
            reminder_notifications=1
        )
        db.add(settings)
        db.commit()

    # Create default categories if none exist
    existing_cats = db.query(Category).filter(Category.user_id == user.id).all()
    cat_map = {c.name: c for c in existing_cats}

    default_categories = [
        {"name": "Work", "description": "Professional projects and work duties", "color": "#4F46E5", "icon": "briefcase"},
        {"name": "Personal", "description": "Everyday personal tasks and health", "color": "#10B981", "icon": "user"},
        {"name": "Study", "description": "Learning, college, and reading goals", "color": "#F59E0B", "icon": "book-open"},
        {"name": "Projects", "description": "Side-projects and software experiments", "color": "#8B5CF6", "icon": "layers"},
    ]

    for cat_data in default_categories:
        if cat_data["name"] not in cat_map:
            new_cat = Category(
                user_id=user.id,
                name=cat_data["name"],
                description=cat_data["description"],
                color=cat_data["color"],
                icon=cat_data["icon"]
            )
            db.add(new_cat)
            db.flush()
            cat_map[cat_data["name"]] = new_cat

    db.commit()

    # Now check if user has tasks. If none, seed realistic demo tasks
    from backend.app.models.task import Task
    has_tasks = db.query(Task).filter(Task.user_id == user.id).first()
    if has_tasks:
        return {"categories_created": len(cat_map), "tasks_created": 0, "message": "User already has tasks."}

    today = date.today()
    sample_tasks = [
        {
            "title": "Design responsive dashboard UI in TaskFlow",
            "description": "Craft modern SaaS layout with sidebar, statistics overview, and accessible task modal.",
            "category_name": "Work",
            "status": "in_progress",
            "priority": "high",
            "due_date": today,
            "due_time": time(17, 0),
            "is_important": True,
            "tags": ["frontend", "ui", "responsive"]
        },
        {
            "title": "Build FastAPI JWT authentication API",
            "description": "Implement user registration, password hashing with bcrypt, and secure bearer token verification.",
            "category_name": "Projects",
            "status": "completed",
            "priority": "urgent",
            "due_date": today - timedelta(days=1),
            "due_time": time(14, 30),
            "is_important": True,
            "tags": ["backend", "api", "security"]
        },
        {
            "title": "Review MySQL database schema & indexing",
            "description": "Verify foreign key constraints, UTF8mb4 character set, and query performance indexes.",
            "category_name": "Projects",
            "status": "completed",
            "priority": "medium",
            "due_date": today - timedelta(days=2),
            "due_time": time(11, 0),
            "is_important": False,
            "tags": ["database", "mysql"]
        },
        {
            "title": "Submit college Software Engineering assignment",
            "description": "Prepare architecture diagram, project report, and documentation slides for submission.",
            "category_name": "Study",
            "status": "pending",
            "priority": "urgent",
            "due_date": today,
            "due_time": time(23, 59),
            "is_important": True,
            "tags": ["college", "assignment"]
        },
        {
            "title": "Study Modern Web & Accessibility guidelines",
            "description": "Go through semantic HTML, ARIA dialog accessibility, keyboard navigation and color contrast.",
            "category_name": "Study",
            "status": "pending",
            "priority": "medium",
            "due_date": today + timedelta(days=1),
            "due_time": time(18, 0),
            "is_important": False,
            "tags": ["a11y", "study"]
        },
        {
            "title": "Grocery shopping and weekend meal preparation",
            "description": "Pick up fresh produce, groceries, and prep meals for the upcoming work week.",
            "category_name": "Personal",
            "status": "pending",
            "priority": "low",
            "due_date": today + timedelta(days=3),
            "due_time": time(10, 0),
            "is_important": False,
            "tags": ["lifestyle", "home"]
        },
        {
            "title": "Deploy TaskFlow application to production server",
            "description": "Setup Uvicorn reverse proxy, verify MySQL connectivity, and test end-to-end task workflows.",
            "category_name": "Work",
            "status": "pending",
            "priority": "high",
            "due_date": today + timedelta(days=2),
            "due_time": time(16, 0),
            "is_important": True,
            "tags": ["devops", "deploy"]
        },
        {
            "title": "Read Chapter 4 of Clean Architecture",
            "description": "Take notes on dependency inversion and clean separation of concerns between layers.",
            "category_name": "Study",
            "status": "pending",
            "priority": "low",
            "due_date": today + timedelta(days=5),
            "due_time": None,
            "is_important": False,
            "tags": ["books", "architecture"]
        }
    ]

    created_count = 0
    for st in sample_tasks:
        cat_id = cat_map[st["category_name"]].id if st["category_name"] in cat_map else None
        task_create_data = TaskCreate(
            title=st["title"],
            description=st["description"],
            status=st["status"],
            priority=st["priority"],
            category_id=cat_id,
            due_date=st["due_date"],
            due_time=st["due_time"],
            is_important=st["is_important"],
            tags=st["tags"]
        )
        create_task(db, user.id, task_create_data)
        created_count += 1

    return {
        "categories_created": len(cat_map),
        "tasks_created": created_count,
        "message": f"Successfully seeded {created_count} realistic tasks and {len(cat_map)} categories."
    }
