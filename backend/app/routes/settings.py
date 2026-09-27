from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.settings import UserSettings
from backend.app.auth.deps import get_current_user
from backend.app.schemas.settings import UserSettingsUpdate, UserSettingsOut
from backend.app.schemas.common import APIResponse
from backend.app.utils.response import success_response

router = APIRouter(prefix="/settings", tags=["User Settings"])


@router.get("", response_model=APIResponse[UserSettingsOut])
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve personal settings for the authenticated user."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return success_response(
        data=UserSettingsOut.model_validate(settings).model_dump(),
        message="Settings retrieved successfully."
    )


@router.put("", response_model=APIResponse[UserSettingsOut])
def update_user_settings(
    settings_in: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update personal settings (theme, default priority, tasks per page, etc.)."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.flush()

    if settings_in.theme is not None:
        settings.theme = settings_in.theme
    if settings_in.default_task_priority is not None:
        settings.default_task_priority = settings_in.default_task_priority
    if settings_in.default_task_status is not None:
        settings.default_task_status = settings_in.default_task_status
    if settings_in.tasks_per_page is not None:
        settings.tasks_per_page = settings_in.tasks_per_page
    if settings_in.show_completed_tasks is not None:
        settings.show_completed_tasks = 1 if settings_in.show_completed_tasks else 0
    if settings_in.email_notifications is not None:
        settings.email_notifications = 1 if settings_in.email_notifications else 0
    if settings_in.reminder_notifications is not None:
        settings.reminder_notifications = 1 if settings_in.reminder_notifications else 0

    db.commit()
    db.refresh(settings)

    return success_response(
        data=UserSettingsOut.model_validate(settings).model_dump(),
        message="Settings updated successfully."
    )
