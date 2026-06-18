from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.store import auth_store, get_current_user
from app.models.schemas import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    UserResponse
)

router = APIRouter(tags=["auth"])
bearer_scheme = HTTPBearer()


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest):

    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters."
        )

    try:
        user = auth_store.create_user(
            name=request.name,
            email=request.email,
            password=request.password
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc

    session = auth_store.create_session(
        user["id"]
    )

    return AuthResponse(
        token=session["token"],
        user=UserResponse(**user)
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):

    user = auth_store.get_user_by_email(
        request.email
    )

    if not user or not auth_store.verify_password(
        user,
        request.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    session = auth_store.create_session(
        user["id"]
    )

    return AuthResponse(
        token=session["token"],
        user=UserResponse(
            **auth_store.public_user(user)
        )
    )


@router.get("/me", response_model=UserResponse)
def me(user: dict = Depends(get_current_user)):

    return UserResponse(**user)


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    auth_store.delete_session(
        credentials.credentials
    )

    return {
        "logged_out": True
    }
