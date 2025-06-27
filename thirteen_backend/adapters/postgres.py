from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from thirteen_backend import config


def db_dsn(
    dialect: str,
    user: str,
    host: str,
    port: int,
    database: str,
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


engine = create_async_engine(
    db_dsn(
        dialect=config.BACKEND_DB_DIALECT,
        user=config.BACKEND_DB_USER,
        host=config.BACKEND_DB_HOST,
        port=config.BACKEND_DB_PORT,
        database=config.BACKEND_DB_NAME,
        driver=config.BACKEND_DB_DRIVER,
        password=config.BACKEND_DB_PASSWORD,
    ),
    poolclass=None,
)

_async_session_maker = async_sessionmaker(engine)


def get_session() -> AsyncSession:
    return _async_session_maker()
