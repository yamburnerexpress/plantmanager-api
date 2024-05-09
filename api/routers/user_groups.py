from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session
from typing import Annotated
from api import crud, models, schemas
from api.database import get_db
from api.auth.controller import jwt_required, get_current_user

router = APIRouter(
    prefix="/api/usergroups",
    dependencies=[Depends(jwt_required)]
)

@router.post("/create/", response_model=schemas.UserGroupResponse)
def create_group(current_user: Annotated[schemas.User, Depends(get_current_user)], user_group: schemas.UserGroupInput, db: Session = Depends(get_db)):
    if user_group.is_default:
        if crud.get_has_default_group(db=db, current_user=current_user):
            raise HTTPException(status_code=400, detail="User already has a default group")
    res = crud.create_user_group(db=db, group=user_group, current_user=current_user)
    return res

@router.post("/{group_id}/update/")
def create_group(current_user: Annotated[schemas.User, Depends(get_current_user)], group_id: int, user_group: schemas.UserGroupBase, db: Session = Depends(get_db)):
    if not crud.get_user_group_by_id(db=db, group_id=group_id, current_user=current_user):
        raise HTTPException(status_code=404, detail="Group not found for current user")
    crud.update_user_group(db=db, group_id=group_id, group=user_group, current_user=current_user)
    return JSONResponse(status_code=200, content={"message": "Group updated successfully"})
