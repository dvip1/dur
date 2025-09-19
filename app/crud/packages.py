from sqlalchemy.orm import Session
from app.schemas.packages import PackageBase  
from app.database.models.packages import Package

def create_package(db:Session, package: PackageBase, user_id: int )->Package: 
    """
     Create a new package in the database.

    Args:
        db (Session): SQLAlchemy session.
        package (schema.package.PackageBase): Pydantic schema with package input data.
        user_id (int): ID of the user creating the package.

    Returns:
        Package: The newly created Package object.
    """
    db_package = Package(name=package.name, description= package.description, repo_url= str(package.repo_url), 
                         license = package.license, 
                         homepage= str(package.homepage),
                         created_by = user_id 
                         )
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package
