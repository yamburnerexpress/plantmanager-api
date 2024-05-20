import datetime
import string
import random
from sqlalchemy import update, desc, case
from sqlalchemy.orm import Session
from . import models, schemas
from api.auth.controller import get_hashed_password


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def invite_user(db: Session, user: schemas.UserBase):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db_invite_code = models.UserInviteCodes(
        username=user.username,
        invite_code=code,
        created_at=datetime.datetime.utcnow()
    )
    db.add(db_invite_code)
    db.commit()
    db.refresh(db_invite_code)
    return db_invite_code

def get_existing_invite(db: Session, user: schemas.UserBase):
    return db.query(models.UserInviteCodes.invite_code).filter(models.UserInviteCodes.username == user.username).first()

def get_invited_users(db: Session):
    return db.query(models.UserInviteCodes).all()

def create_user(db: Session, user: schemas.UserIn):
    hashed_password = get_hashed_password(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        created_at=datetime.datetime.utcnow(),
        admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def change_my_password(db: Session, password: schemas.ChangePasswordInput, current_user: int):
    hashed_password = get_hashed_password(password.newPassword)
    u = update(models.User) \
        .values({"hashed_password": hashed_password}) \
        .where(models.User.id == current_user)
    db.execute(u)
    db.commit()
    return db.query(models.User).filter(models.User.id == current_user).first()

def create_plant(db: Session, plant: schemas.PlantBase):
    db_plant = models.Plant(
        name=plant.name,
        scientific_name=plant.scientific_name,
        type=plant.type,
        created_at=datetime.datetime.utcnow(),
        watering_freq=plant.watering_freq,
        watering_period=plant.watering_period,
        watering_time=plant.watering_time,
        sun_requirement=plant.sun_requirement,
        external_link=plant.external_link
    )
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

def update_plant(db: Session, plant: schemas.PlantResponse):
    u = update(models.Plant) \
        .values(plant.dict()) \
        .where(models.Plant.id == plant.id)
    db.execute(u)
    db.commit()
    return db.query(models.Plant).filter(models.Plant.id==plant.id).first()

def get_plants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Plant).offset(skip).limit(limit).all()

def get_plant_by_id(db: Session, plant_id: int):
    return db.query(models.Plant).filter(models.Plant.id == plant_id).first()

def create_user_plant(db: Session, user_plant: schemas.UserPlantBase, current_user):
    max_order = db.query(models.UserPlant.order).filter(models.UserPlant.user_id == current_user).order_by(desc(models.UserPlant.order)).first()
    new_order = 1 if not max_order else max_order.order + 1
    default_group = db.query(models.UserGroup.id) \
        .filter(models.UserGroup.user_id == current_user) \
        .filter(models.UserGroup.is_default) \
        .first()
    db_user_plant = models.UserPlant(
        user_id=current_user,
        plant_id=user_plant.plant_id,
        nickname=user_plant.nickname,
        count=user_plant.count,
        order=new_order,
        user_group_id=user_plant.user_group_id if user_plant.user_group_id is not None else default_group.id,
        image_path=user_plant.image_path,
        created_at=datetime.datetime.utcnow()
    )
    db.add(db_user_plant)
    db.commit()
    db.refresh(db_user_plant)
    return db_user_plant

def update_user_plant(db: Session, plant_id: int, user_plant: schemas.UserPlantUpdate, current_user):
    u = update(models.UserPlant) \
        .values(user_plant.dict(exclude_none=True)) \
        .where(models.UserPlant.id == plant_id) \
        .where(models.UserPlant.user_id == current_user)
    db.execute(u)
    db.commit()
    return db.query(models.UserPlant).filter(models.UserPlant.id == plant_id).first()

def get_user_plants(db: Session, current_user):
    res = db.query(models.UserPlant) \
        .filter(models.UserPlant.user_id == current_user) \
        .order_by(models.UserPlant.plant_data.name).all()
    return res

def get_user_plant_by_id(db: Session, plant_id: int, current_user):
    res = db.query(models.UserPlant) \
        .filter(models.UserPlant.user_id == current_user) \
        .filter(models.UserPlant.id == plant_id) \
        .first()
    return res

def water_plants(db: Session, plant_ids: schemas.WaterPlantsInput, current_user):
    u = update(models.UserPlant) \
        .values({"last_watered": datetime.datetime.utcnow()}) \
        .where(models.UserPlant.id.in_(plant_ids.plant_ids)) \
        .where(models.UserPlant.user_id == current_user)
    db.execute(u)
    db.commit()
    return plant_ids

def delete_user_plant(db: Session, plant_id: int, current_user):
    u = update(models.UserPlant) \
        .values({"deleted_at": datetime.datetime.utcnow()}) \
        .where(models.UserPlant.id == plant_id) \
        .where(models.UserPlant.user_id == current_user)
    result = db.execute(u)
    db.commit()
    return result

def create_user_group(db: Session, group: schemas.UserGroupInput, current_user):
    db_group = models.UserGroup(
        name=group.name,
        user_id=current_user,
        is_default=group.is_default,
        created_at=datetime.datetime.utcnow()
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_user_group(db: Session, group_id: int, group: schemas.UserGroupBase, current_user: schemas.User):
    u = update(models.UserGroup) \
        .values({"name": group.name}) \
        .where(models.UserGroup.id == group_id) \
        .where(models.UserGroup.user_id == current_user)
    db.execute(u)
    db.commit()
    return u

def get_user_group_by_id(db: Session, group_id: int, current_user: schemas.User):
    res = db.query(models.UserGroup) \
        .filter(models.UserGroup.user_id == current_user) \
        .filter(models.UserGroup.id == group_id) \
        .first()
    return res

def get_user_groups(db: Session, current_user):
    res = db.query(models.UserGroup) \
        .filter(models.UserGroup.user_id == current_user) \
        .order_by(
            case((models.UserGroup.is_default == True, 1), else_=0),
            models.UserGroup.name
        ) \
        .all()
    return res

def get_has_default_group(db: Session, current_user):
    default_group = db.query(models.UserGroup.id) \
        .filter(models.UserGroup.user_id == current_user) \
        .filter(models.UserGroup.is_default) \
        .order_by(models.UserGroup.name) \
        .first()
    return default_group is not None

def create_user_plant_note(db: Session, plant_id: int, note: schemas.UserPlantNoteBase, current_user):
    db_note = models.UserPlantNotes(
        user_plant_id=plant_id,
        user_id=current_user,
        created_at=datetime.datetime.utcnow(),
        note=note.note
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_user_plant_notes(db: Session, plant_id: models.UserPlantNotes.user_plant_id, current_user: int):
    notes = db.query(models.UserPlantNotes) \
        .filter(models.UserPlantNotes.user_plant_id == plant_id) \
        .filter(models.UserPlantNotes.user_id == current_user) \
        .order_by(desc(models.UserPlantNotes.created_at)) \
        .all()
    return notes
