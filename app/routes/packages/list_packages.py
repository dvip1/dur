
from app.routes.packages.packages import router
from app import dependencies as deps
from app.core.routes import Routes # Your route configuration class
from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.schemas import user as user_schema
from sqlalchemy.orm import Session
from app.database.models.packages import Package

@router.get(Routes.Packages.default)
async def list_packages(request: Request, 
                        current_user: user_schema.UserPublic = Depends(deps.get_current_user),  
                              db: Session = Depends(deps.get_db)):
    packages = db.query(Package).all()
    return {"packages": [pkg.name for pkg in packages]}