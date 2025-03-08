from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.models import Base
# from app.database import SQLALCHEMY_DATABASE_URL
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/user_db"

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(SQLALCHEMY_DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

asyncio.run(run_migrations_online())