import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    url=DATABASE_URL,
    pool_size=20,
    max_overflow=30,
)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

# "postgresql+asyncpg://postgres:postgres@localhost:6432/postgres"
