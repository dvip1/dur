import datetime
from sqlalchemy import JSON, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    repo_url = Column(String, unique=True, index=True, nullable=False)
    license = Column(String, nullable=True)
    homepage = Column(String, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    creator = relationship("User", back_populates="packages") 
    versions = relationship("PackageVersion", back_populates="package", cascade="all, delete-orphan")
     
class PackageVersion(Base):
    __tablename__ = "package_versions"

    id = Column(Integer, primary_key=True, index=True)

    # The data parsed from dur.json
    version = Column(String, nullable=False)
    release = Column(Integer, nullable=False)
    source_url = Column(String, nullable=False)

    package_metadata = Column(JSON) 

    # The tag from the recipe repository
    git_tag = Column(String, nullable=False)
    
    published_at = Column(DateTime, default= datetime.datetime.now(datetime.timezone.utc))

    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False, index=True)

    package = relationship("Package", back_populates="versions")

    __table_args__ = (
        UniqueConstraint('package_id', 'version', 'release', name='_package_version_release_uc'),
    )