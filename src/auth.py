from os import getenv
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes


KEYCLOAK_HOST = getenv("KEYCLOAK_HOST", "http://localhost:8080")
KEYCLOAK = f"{KEYCLOAK_HOST}/auth/realms/master/"


keycloak_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=KEYCLOAK + "protocol/openid-connect/auth", tokenUrl=KEYCLOAK + "protocol/openid-connect/token"
)


async def parse_bearer_token(security_scopes: SecurityScopes, token: str = Depends(keycloak_scheme)):
    # FIXME: parse the token
    pass
