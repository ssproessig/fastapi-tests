from os import getenv
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
from keycloak import KeycloakOpenID


class AuthError(Exception):
    def __init__(self, message, status_code=403):
        self.message = {"message": message}
        self.status_code = status_code


try:
    KEYCLOAK_HOST = getenv("KEYCLOAK_HOST", "http://localhost:8080/auth/")
    KEYCLOAK_REALM = getenv("KEYCLOAK_REALM", "master")

    print(f"Configuring Keycloak {KEYCLOAK_HOST} using realm '{KEYCLOAK_REALM}'...")
    keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_HOST, realm_name=KEYCLOAK_REALM, client_id="admin")
    KEYCLOAK_WELL_KNOW = keycloak_openid.well_know()
    KEYCLOAK_CERTS = keycloak_openid.certs()

    oAuthBearer = OAuth2AuthorizationCodeBearer(
        authorizationUrl=KEYCLOAK_WELL_KNOW['authorization_endpoint'], tokenUrl=KEYCLOAK_WELL_KNOW['token_endpoint']
    )

except Exception as e:
    print(f"...failed: {e}. Endpoints with Authorization will not work.")

    def oAuthBearer(): raise AuthError("Keycloak not set up correctly!", 500)


async def parse_bearer_token(security_scopes: SecurityScopes, token: str = Depends(oAuthBearer)):
    try:
        token_info = keycloak_openid.decode_token(
            token, key=KEYCLOAK_CERTS, options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_exp": True,
                "verify_nbf": True
            }
        )
    except Exception as e:
        raise AuthError(f"JWT error: {e}")

    for scope in security_scopes.scopes:
        if scope not in token_info['scope']:
            raise AuthError(
                f"You don't have access to this resource. '{' '.join(security_scopes.scopes)}' scope(s) required."
            )

    return token_info
