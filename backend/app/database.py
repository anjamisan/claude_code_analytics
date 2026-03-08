from sqlmodel import create_engine, SQLModel, Session
from backend.app.config import settings

# Import all models so SQLModel.metadata knows about them
import backend.app.models.models as _models  # noqa: F401


# Create engine with proper configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.FASTAPI_DEBUG,
    future=True,
    pool_pre_ping=True,  # Verify connections before using
)


def create_db_and_tables():
    """Create all database tables on startup"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for FastAPI to get database session"""
    with Session(engine) as session:
        yield session


async def close_db_connection():
    """Close the database engine connection"""
    engine.dispose()