from fastapi import APIRouter
from app.core.routes import Routes

router = APIRouter(
    prefix=Routes.Packages.root,
    tags=['packages'],
)