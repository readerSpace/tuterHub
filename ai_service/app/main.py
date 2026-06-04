from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine
from .routers import ai, health, students


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title='TutorHub AI Service',
    version='1.0.0',
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(students.router, tags=['Students'])
app.include_router(ai.router, prefix='/ai', tags=['AI'])
