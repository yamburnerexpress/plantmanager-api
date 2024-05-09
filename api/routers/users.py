from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from api import crud, schemas
from api.database import get_db
from api.auth.controller import jwt_required, get_current_user

router = APIRouter(
    prefix="/api/users",
)

@router.get("/", response_model=list[schemas.User])  # , dependencies=[Depends(jwt_required)]
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}/", response_model=schemas.User, dependencies=[Depends(jwt_required)])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/register/", response_model=schemas.User)
async def post_user(user: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    current_user = crud.create_user(db=db, user=user)
    group = schemas.UserGroupInput.parse_obj({"is_default": True})
    crud.create_user_group(db=db, group=group, current_user=current_user.id)
    return current_user

@router.get("/me", dependencies=[Depends(jwt_required)])
async def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user
