import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.routes import (
    auth_router,
    tasks_router,
    categories_router,
    tags_router,
    settings_router
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("taskflow")

# Ensure all tables exist in database on startup
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")
except Exception as e:
    logger.warning(f"Database connection notice: {e}")

app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    version=settings.VERSION,
    description="Production-Ready Full-Stack Task & Productivity Management REST API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers for Consistent JSON Responses
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else "Request error",
            "data": exc.detail if not isinstance(exc.detail, str) else None
        },
        headers=exc.headers
    )


from fastapi.encoders import jsonable_encoder


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert FastAPI/Pydantic validation errors into clean, friendly human messages."""
    error_messages = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        msg = err.get("msg", "Invalid value")
        # Make error friendly
        if "Field required" in msg:
            error_messages.append(f"'{field}' is required.")
        elif "String should have at least" in msg:
            error_messages.append(f"'{field}' is too short.")
        elif "value is not a valid email" in msg:
            error_messages.append("Please enter a valid email address.")
        else:
            clean_msg = msg.replace("Value error, ", "")
            error_messages.append(f"{field}: {clean_msg}" if field else clean_msg)

    friendly_summary = "; ".join(error_messages) if error_messages else "Invalid input data provided."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": friendly_summary,
            "data": jsonable_encoder(exc.errors())
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred. Please try again shortly.",
            "data": None
        }
    )


# Health Check
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["Health"])
def health_check():
    """Service health and database connectivity check."""
    from sqlalchemy import text
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status
    }


# Include Modular Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks_router, prefix=settings.API_V1_PREFIX)
app.include_router(categories_router, prefix=settings.API_V1_PREFIX)
app.include_router(tags_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)

# Serve Frontend files statically if the frontend directory exists
current_file_path = Path(__file__).resolve()
workspace_root = current_file_path.parents[2]
frontend_dir = workspace_root / "frontend"

if frontend_dir.exists() and frontend_dir.is_dir():
    # Mount css, js, assets directories
    app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))
