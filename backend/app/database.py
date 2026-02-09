from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.config import get_settings

settings = get_settings()

# Log database connection type
db_scheme = settings.DATABASE_URL.split("://")[0] if "://" in settings.DATABASE_URL else "unknown"
print(f"DATABASE: Connecting using {db_scheme} dialect")

# Configure engine based on database type
is_sqlite = "sqlite" in settings.DATABASE_URL

engine_kwargs = {
    "echo": settings.DB_ECHO,
}

if is_sqlite:
    # SQLite specific config
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = __import__('sqlalchemy.pool', fromlist=['StaticPool']).StaticPool
else:
    # PostgreSQL/Other database config
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()