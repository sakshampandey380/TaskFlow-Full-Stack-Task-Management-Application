from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "Operation successful", status_code: int = 200) -> dict:
    """Standard success JSON response envelope."""
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(message: str = "An error occurred", status_code: int = 400, data: Any = None) -> JSONResponse:
    """Standard error JSON response envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": data
        }
    )
