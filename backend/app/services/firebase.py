import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

_firebase_app = None
_bearer = HTTPBearer()


def _get_app():
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.ApplicationDefault()
        _firebase_app = firebase_admin.initialize_app(
            cred, {"projectId": settings.firebase_project_id}
        )
    return _firebase_app


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> dict:
    _get_app()
    try:
        decoded = auth.verify_id_token(credentials.credentials)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
