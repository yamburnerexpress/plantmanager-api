from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
from api import crud, models, schemas
from api.database import get_db
from api.auth.controller import jwt_required, get_current_user

router = APIRouter(
    prefix="/api/userplants",
    dependencies=[Depends(jwt_required)]
)

@router.post("/create/")
async def create_plant(current_user: Annotated[schemas.User, Depends(get_current_user)], user_plant: schemas.UserPlantBase, db: Session = Depends(get_db)):
    res = crud.create_user_plant(db=db, user_plant=user_plant, current_user=current_user)
    return {"id": res.id}

@router.post("/{plant_id}/update/", response_model=schemas.UserPlantInfoResponse)
async def update_user_plant(current_user: Annotated[schemas.User, Depends(get_current_user)], plant_id: int, user_plant: schemas.UserPlantUpdate, db: Session = Depends(get_db)):
    res = crud.update_user_plant(db=db, plant_id=plant_id, user_plant=user_plant, current_user=current_user)
    return res

@router.get("/", response_model=list[schemas.UserDashboardGroup])  # schemas.UserPlantInfoResponse
async def get_user_plants(current_user: Annotated[schemas.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    res = crud.get_user_groups(db=db, current_user=current_user)
    return res

@router.get("/{plant_id}/", response_model=schemas.UserPlantInfoResponse)
async def get_user_plant_by_id(plant_id: int, current_user: Annotated[schemas.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    return crud.get_user_plant_by_id(db=db, plant_id=plant_id, current_user=current_user)

@router.post("/water/")
async def water_plants(plant_ids: schemas.WaterPlantsInput, current_user: Annotated[schemas.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    plants_watered = crud.water_plants(db=db, plant_ids=plant_ids, current_user=current_user)
    return {"plants_watered": plants_watered}

@router.post("/{plant_id}/notes/")
async def post_user_plant_note(
        plant_id: int,
        note: schemas.UserPlantNoteBase,
        current_user: Annotated[schemas.User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)]
):
    q = crud.create_user_plant_note(db=db, plant_id=plant_id, note=note, current_user=current_user)
    if not q:
        raise HTTPException(status_code=500, detail="Could not complete request")
    return JSONResponse(status_code=200, content={"message": "Note created successfully"})

@router.get("/{plant_id}/notes/", response_model=list[schemas.UserPlantNoteResponse])
async def get_user_plant_notes(
        plant_id: int,
        current_user: Annotated[int, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)]
):
    q = crud.get_user_plant_notes(db=db, plant_id=plant_id, current_user=current_user)
    return q

@router.delete("/{plant_id}/delete/")
async def delete_user_plant(
        plant_id: int,
        current_user: Annotated[int, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)]
):
    q = crud.delete_user_plant(db=db, plant_id=plant_id, current_user=current_user)
    if not q:
        raise HTTPException(status_code=500, detail="Could not complete request")
    return JSONResponse(status_code=200, content={"message": "User plant deleted successfully"})
