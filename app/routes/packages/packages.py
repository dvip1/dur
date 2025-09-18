from fastapi import APIRouter, Request, Depends
from app.database.models.packages import Package
from app.database.models.user import User
from app.dependencies import get_current_user
from app import dependencies as deps
from app.schemas import user as user_schema
from app.core.routes import Routes # Your route configuration class
from app.schemas.packages import PackageBase as package_schema
from sqlalchemy.orm import Session

router = APIRouter(
    prefix= Routes.Packages.root,
    tags=['packages']
)

@router.get(Routes.Packages.default)
async def list_packages(request: Request, current_user: user_schema.UserPublic = Depends(deps.get_current_user),     db: Session = Depends(deps.get_db)):
    packages = db.query(Package).all()
    return {"packages": [pkg.name for pkg in packages]}


@router.post(Routes.Packages.default)
async def create_packages(data: package_schema, 
                           current_user: user_schema.UserPublic = Depends(deps.get_current_user)
                           ): 
    pass

