from backend.app.routes.auth import router as auth_router
from backend.app.routes.tasks import router as tasks_router
from backend.app.routes.categories import router as categories_router
from backend.app.routes.tags import router as tags_router
from backend.app.routes.settings import router as settings_router

__all__ = [
    "auth_router",
    "tasks_router",
    "categories_router",
    "tags_router",
    "settings_router"
]
