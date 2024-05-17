from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from typing import Annotated
from sqlalchemy.orm import Session
from api import crud, schemas
from api.database import get_db
from api.auth.controller import verify_password, jwt_required, get_current_user

router = APIRouter(
    prefix="/api/users",
)

@router.get("/", response_model=list[schemas.User], dependencies=[Depends(jwt_required)])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me/", dependencies=[Depends(jwt_required)])
async def read_users_me(current_user: Annotated[int, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    db_user = crud.get_user(db, user_id=current_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user

@router.post("/me/changepassword/", dependencies=[Depends(jwt_required)])
async def change_my_password(password: schemas.ChangePasswordInput, current_user: Annotated[int, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    user = crud.get_user(db, current_user)
    hashed_pass = user.hashed_password
    if not verify_password(password.oldPassword, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
    q = crud.change_my_password(db=db, password=password, current_user=current_user)
    if not q:
        raise HTTPException(status_code=500, detail="Could not complete request")
    return JSONResponse(status_code=200, content={"message": "Password changed successfully"})

@router.post("/invite/", response_model=schemas.UserInviteCode, dependencies=[Depends(jwt_required)])
async def invite_user(user: schemas.UserBase, db: Annotated[Session, Depends(get_db)]):
    existing_invite = crud.get_existing_invite(db=db, user=user)
    if existing_invite:
        raise HTTPException(status_code=400, detail="User already invited")
    db_invite_code = crud.invite_user(db=db, user=user)
    return db_invite_code

@router.get("/invites/", response_model=list[schemas.UserInviteCode], dependencies=[Depends(jwt_required)])
async def get_invited_users(db: Annotated[Session, Depends(get_db)]):
    return crud.get_invited_users(db=db)

@router.get("/{user_id}/", response_model=schemas.User, dependencies=[Depends(jwt_required)])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/register/", response_model=schemas.User)
async def post_user(user: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    existing_invite = crud.get_existing_invite(db=db, user=user)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if not existing_invite or user.invite_code != existing_invite.invite_code:
        raise HTTPException(status_code=400, detail="Invalid invite code")
    current_user = crud.create_user(db=db, user=user)
    group = schemas.UserGroupInput.parse_obj({"is_default": True})
    crud.create_user_group(db=db, group=group, current_user=current_user.id)
    return current_user


