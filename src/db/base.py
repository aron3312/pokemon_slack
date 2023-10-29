from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src import config

sync_engine = create_engine(
    config.DB_DSN
)
engine = create_async_engine(
    config.DB_DSN,
    echo=config.DB_ECHO,
    future=True,
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession, future=True)
metadata = MetaData()
Base = declarative_base(metadata=metadata)
