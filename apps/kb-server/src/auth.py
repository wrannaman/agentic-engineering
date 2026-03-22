"""Bearer token authentication — dead simple."""

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import config

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify the bearer token. Raises 401 if invalid."""
    if not config.KB_AUTH_TOKEN:
        return  # no auth configured = open access
    if credentials.credentials != config.KB_AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
