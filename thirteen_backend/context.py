from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis


class AuthorizationContext:
    def __init__(
        self,
        unified_user_id: str | None = None,
        jwt_claims: dict[str, Any] | None = None,
    ):
        self.unified_user_id = unified_user_id
        self.jwt_claims = jwt_claims


@dataclass
class RequestContext:
    request_id: str
    client_ip_address: Optional[str] = None
    endpoint: Optional[str] = None
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)

    @property
    def user_agent(self) -> Optional[str]:
        for k in ["User-Agent", "user-agent", "User-agent"]:
            if k in self.headers:
                return self.headers[k]
        return None

    @property
    def authorization_header(self) -> Optional[str]:
        for k in ["Authorization", "authorization"]:
            if k in self.headers:
                return self.headers[k]

        return None


class AbstractContext(ABC):
    db_session: "AsyncSession"
    auth_context: "AuthorizationContext | None"

    @property
    @abstractmethod
    def redis_client(self) -> Redis: ...


class APIRequestContext(AbstractContext):
    def __init__(
        self,
        request: "Request | None",
        db_session: "AsyncSession",
        auth_context: "AuthorizationContext | None",
    ) -> None:
        self.request = request
        self.db_session = db_session
        self.auth_context = auth_context

        @property
        def redis_client(self) -> Redis:
            redis_client: Redis = self.request.app.state.redis_client
            return redis_client
