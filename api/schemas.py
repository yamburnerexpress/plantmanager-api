import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserInviteCode(UserBase):
    invite_code: str

class UserIn(UserInviteCode):
    password: str

class UserChangePassword(UserIn):
    newPassword: str

class User(UserBase):
    id: int
    created_at: Optional[datetime.datetime]
    last_seen: Optional[datetime.datetime]

    class Config:
        orm_model = True

class ChangePasswordInput(BaseModel):
    oldPassword: str
    newPassword: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class WateringFrequencyPeriodType(str, Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"

class WateringTimeType(str, Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"

class SunRequirementType(str, Enum):
    SHADE = "SHADE"
    PART_SHADE = "PART_SHADE"
    FULL_SUN = "FULL_SUN"

class PlantType(str, Enum):
    TREE = "TREE"
    LEAFY_PLANT = "LEAFY_PLANT"
    FLOWER = "FLOWER"
    SUCCULENT = "SUCCULENT"
    HERB = "HERB"
    VEGETABLE = "VEGETABLE"


class WateringInfo(BaseModel):
    watering_freq: Optional[int] = None
    watering_period: Optional[WateringFrequencyPeriodType] = None
    watering_time: Optional[WateringTimeType] = None


class PlantBase(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    type: Optional[PlantType] = None
    watering_freq: Optional[int] = None
    watering_period: Optional[WateringFrequencyPeriodType] = None
    watering_time: Optional[WateringTimeType] = None
    sun_requirement: Optional[SunRequirementType] = None
    external_link: Optional[str] = None


class PlantResponse(PlantBase):
    id: int

    class Config:
        orm_model = True

class PlantId(BaseModel):
    id: int


class UserGroupBase(BaseModel):
    name: Optional[str] = ""

class UserGroupInput(UserGroupBase):
    is_default: bool

class UserGroupResponse(UserGroupInput):
    created_at: datetime.datetime
    id: int


class UserPlantBase(BaseModel):
    plant_id: int
    nickname: Optional[str] = None
    image_path: Optional[str]
    count: Optional[int] = 1
    user_group_id: Optional[int] = None

class UserPlantUpdate(BaseModel):
    nickname: Optional[str] = None
    order: Optional[int] = None
    count: Optional[int] = None
    image_path: Optional[str] = None
    user_group_id: Optional[int] = None

class UserPlantDBInput(UserPlantBase):
    user_id: int
    count: int

class UserPlantResponse(UserPlantDBInput):
    id: int

class UserPlantInfoResponse(BaseModel):
    id: int
    nickname: Optional[str]
    order: int
    count: int
    image_path: Optional[str]
    last_watered: Optional[datetime.datetime]
    plant_data: PlantResponse

    class Config:
        orm_model = True

class WaterPlantsInput(BaseModel):
    plant_ids: List[int]

class UserDashboardGroup(UserGroupResponse):
    plants: List[UserPlantInfoResponse] = []

class UserPlantNoteBase(BaseModel):
    note: str

class UserPlantNoteResponse(UserPlantNoteBase):
    id: int
    created_at: datetime.datetime
