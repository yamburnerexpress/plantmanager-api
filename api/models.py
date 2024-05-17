import enum
from sqlalchemy import Boolean, Column, ForeignKey, Text, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base
from api.schemas import WateringFrequencyPeriodType, WateringTimeType, SunRequirementType, PlantType

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    admin = Column(Boolean)
    hashed_password = Column(String(128))
    created_at = Column(DateTime)
    last_seen = Column(DateTime)


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    scientific_name = Column(String(255))
    type = Column(Enum(PlantType))
    created_at = Column(DateTime)
    watering_freq = Column(Integer)
    watering_period = Column(Enum(WateringFrequencyPeriodType))
    watering_time = Column(Enum(WateringTimeType))
    sun_requirement = Column(Enum(SunRequirementType))
    external_link = Column(Text)


class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_default = Column(Boolean, default=False)
    name = Column(String(128))
    created_at = Column(DateTime)
    deleted_at = Column(DateTime)
    plants = relationship("UserPlant", backref="plants")


class UserPlant(Base):
    __tablename__ = "user_plants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plant_id = Column(Integer, ForeignKey("plants.id"))
    nickname = Column(String(128))
    count = Column(Integer, default=1)
    order = Column(Integer)
    image_path = Column(Text)
    created_at = Column(DateTime)
    user_group_id = Column(Integer, ForeignKey("user_groups.id"))
    last_watered = Column(DateTime)
    deleted_at = Column(DateTime)
    plant_data = relationship("Plant", backref="plant_data")
    note_data = relationship("UserPlantNotes", backref="note_data")

class UserPlantNotes(Base):
    __tablename__ = "user_plant_notes"
    id = Column(Integer, primary_key=True, index=True)
    user_plant_id = Column(Integer, ForeignKey("user_plants.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)
    deleted_at = Column(DateTime)
    note = Column(Text)

class UserInviteCodes(Base):
    __tablename__ = "user_invite_codes"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    invite_code = Column(String(255), unique=True)
    created_at = Column(DateTime)
