from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from api import crud, models, schemas
from api.auth.controller import verify_password, create_access_token, create_refresh_token, verify_refresh_token
from api.database import get_db

router = APIRouter(prefix="/api/auth")

@router.post("/login/", summary="Create access and refresh tokens for user", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    # print(user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    hashed_pass = user.hashed_password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    token_payload = {
        "sub": None,
        "username": user.username,
        "id": user.id
    }

    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    # response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    # response.set_cookie(key="access_token", value=f"Bearer {access_token}")
    # response.set_cookie(key="refresh_token", value=refresh_token)
    # return response
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.get("/refresh/", status_code=status.HTTP_200_OK)
async def get_new_access_token(token: str):
    refresh_data = verify_refresh_token(token)

    new_access_token = create_access_token(refresh_data)
    return {
        "access_token": new_access_token,
        "token_type": "Bearer",
        "status": status.HTTP_200_OK
    }
