from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.core.routes import Routes # Your route configuration class

router = APIRouter(
    prefix= Routes.Packages.root,
    tags=['packages']
)


