# routes/packages/list_packages.py

from typing import List
from app.routes.packages.packages import router
from app import dependencies as deps
from app.core.routes_version1 import Routes # Your route configuration class
from fastapi import APIRouter, HTTPException, Query, Request, Depends, status
from app.schemas import user as user_schema
from app.schemas.package_version import PackageDetailOut

from app.schemas.packages import PackageOut # Import the output schema
from sqlalchemy.orm import Session
from app.database.models.packages import Package, PackageVersion

@router.get(
    Routes.Packages.default,
    response_model=List[PackageOut], # Defines the successful response structure
    summary="List all packages",
    response_description="A list of all registered packages.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "An unexpected error occurred on the server.",
            "content": {
                "application/json": {
                    "example": {"detail": "Error retrieving packages from the database."}
                }
            },
        },
    },
)
async def list_packages(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=100, description="Max number of records to return"),
):
    """
    ### List available packages with pagination 📦

    Retrieves a list of packages from the system, sorted from newest to oldest.

    - Supports **pagination** using `skip` and `limit` query parameters.
    """
    try:
        packages = (
            db.query(Package)
            .order_by(Package.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return packages
    except Exception as e:
        print(f"Error fetching packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving packages.",
        )



@router.get(
    Routes.Packages.get_by_name, 
    response_model=PackageDetailOut,
    summary="Get a specific package by name",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Package not found"},
    },
)
async def get_package(
    package_name: str,
    db: Session = Depends(deps.get_db),
):
    """
    ### Retrieve a single package by its unique name 🔎

    Fetches the complete details for a specific package, including the
    metadata for its most recently published version.
    """
    package = db.query(Package).filter(Package.name == package_name).first()

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package '{package_name}' not found.",
        )

    latest_version = (
        db.query(PackageVersion)
        .filter(PackageVersion.package_id == package.id)
        .order_by(PackageVersion.published_at.desc())
        .first()
    )
    package.latest_version = latest_version

    return package