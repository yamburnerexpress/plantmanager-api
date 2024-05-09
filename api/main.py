from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from api.routers import auth, users, plants, user_plants, user_groups

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000/",
    "https://plantyard.netlify.app/",
    "https://plantyard.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(plants.router)
app.include_router(user_plants.router)
app.include_router(user_groups.router)
