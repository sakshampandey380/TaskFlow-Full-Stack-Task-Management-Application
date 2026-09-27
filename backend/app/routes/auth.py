from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.settings import UserSettings
from backend.app.schemas.user import UserRegister, UserLogin, UserOut, TokenResponse
from backend.app.schemas.common import APIResponse
from backend.app.auth.security import get_password_hash, verify_password, create_access_token
from backend.app.auth.deps import get_current_user
from backend.app.services.seed_service import seed_user_data
from backend.app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account, seed default categories, and return JWT access token."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in instead."
        )

    # Create new user
    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=get_password_hash(user_in.password),
        is_active=1,
        last_login=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize default settings and demo categories & tasks
    seed_user_data(db, new_user)

    # Generate token
    token = create_access_token(subject=new_user.id)
    user_out = UserOut.model_validate(new_user)

    return success_response(
        data=TokenResponse(access_token=token, token_type="bearer", user=user_out).model_dump(),
        message="Account created successfully! Welcome to TaskFlow.",
        status_code=status.HTTP_201_CREATED
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password to receive JWT access token."""
    user = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is currently inactive. Please contact support."
        )

    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    user_out = UserOut.model_validate(user)

    return success_response(
        data=TokenResponse(access_token=token, token_type="bearer", user=user_out).model_dump(),
        message=f"Welcome back, {user.name}!"
    )


@router.get("/me", response_model=APIResponse[UserOut])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile and details of currently authenticated user."""
    return success_response(
        data=UserOut.model_validate(current_user).model_dump(),
        message="Profile retrieved successfully."
    )


@router.post("/logout", response_model=APIResponse[dict])
def logout(current_user: User = Depends(get_current_user)):
    """Sign out the current user."""
    return success_response(
        data={"user_id": current_user.id},
        message="Successfully logged out."
    )
