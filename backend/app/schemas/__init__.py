from backend.app.schemas.common import APIResponse
from backend.app.schemas.user import UserRegister, UserLogin, UserOut, TokenResponse
from backend.app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from backend.app.schemas.tag import TagCreate, TagOut
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskCompleteToggle
from backend.app.schemas.settings import UserSettingsUpdate, UserSettingsOut
from backend.app.schemas.stats import TaskStatsOut

__all__ = [
    "APIResponse",
    "UserRegister",
    "UserLogin",
    "UserOut",
    "TokenResponse",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryOut",
    "TagCreate",
    "TagOut",
    "TaskCreate",
    "TaskUpdate",
    "TaskOut",
    "TaskCompleteToggle",
    "UserSettingsUpdate",
    "UserSettingsOut",
    "TaskStatsOut",
]
