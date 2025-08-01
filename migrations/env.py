import asyncio
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

load_dotenv()
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def db_dsn(
    dialect: str,
    user: str,
    host: str,
    database: str,
    port: int = 5432,
    driver: str | None = None,
    password: str | None = None,
) -> str:
    scheme = dialect
    if driver:
        scheme += f"+{driver}"
    if password:
        password = f":{password}"
    else:
        password = ""

    return f"{scheme}://{user}{password}@{host}:{port}/{database}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    dialect = os.getenv("BACKEND_DB_DIALECT")
    user = os.getenv("BACKEND_DB_USER")
    host = os.getenv("BACKEND_DB_HOST")
    database = os.getenv("BACKEND_DB_NAME")
    driver = os.getenv("BACKEND_DB_DRIVER")
    password = os.getenv("BACKEND_DB_PASSWORD")
    os.getenv("ENV")
    pg_url = db_dsn(
        dialect=dialect,
        user=user,
        host=host,
        database=database,
        driver=driver,
        password=password,
    )

    config.set_section_option(config.config_ini_section, "sqlalchemy.url", pg_url)
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
