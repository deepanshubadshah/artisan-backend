import sys
import os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context

# Ensure the 'app' directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Base and models
from app.core.database import Base  # Import Base correctly
from app.models import lead  # Ensure models are loaded

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use your model's metadata for autogenerate support
target_metadata = Base.metadata

# Run migrations in 'offline' mode
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Run migrations in 'online' mode
async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async connection."""
    url = config.get_main_option("sqlalchemy.url")
    engine = create_async_engine(url, future=True, echo=True)

    async with engine.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()

def do_run_migrations(connection):
    """Helper function to run migrations."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

# Determine sync or async mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())