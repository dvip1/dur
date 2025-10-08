from fastapi import APIRouter
from app.core.routes_version1 import Routes

router = APIRouter(
    prefix=Routes.Packages.root,
    tags=['packages'],
)