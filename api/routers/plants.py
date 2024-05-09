from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from api import crud, models, schemas
from api.database import get_db
from api.auth.controller import jwt_required, get_current_user

router = APIRouter(
    prefix="/api/plants",
    dependencies=[Depends(get_current_user)]
)

@router.post("/create/", response_model=schemas.PlantResponse)
async def create_plant(plant: schemas.PlantBase, db: Session = Depends(get_db)):
    return crud.create_plant(db=db, plant=plant)

@router.post("/update/", response_model=schemas.PlantId)
async def update_plant(plant: schemas.PlantResponse, db: Session = Depends(get_db)):
    return crud.update_plant(db=db, plant=plant)

@router.get("/", response_model=list[schemas.PlantResponse])
async def get_plants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_plants(db, skip, limit)

@router.get("/{plant_id}/", response_model=schemas.PlantResponse)
async def get_plant_id(plant_id: int, db: Session = Depends(get_db)):
    db_plant = crud.get_plant_by_id(db, plant_id=plant_id)
    if db_plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return db_plant
