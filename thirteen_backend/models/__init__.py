import os
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


for module in os.listdir(os.path.dirname(__file__)):
    if module.endswith(".py") and module != "__init__.py":
        __import__(f"thirteen_backend.models.{module.removesuffix('.py')}")
