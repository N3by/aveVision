from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserSync, UserResponse
from app.services.firebase import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync", response_model=UserResponse)
async def sync_user(
    body: UserSync,
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Upsert Firebase user into Cloud SQL. Call once after every login."""
    if token["uid"] != body.firebase_uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="UID mismatch")
    result = await db.execute(select(User).where(User.firebase_uid == body.firebase_uid))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            firebase_uid=body.firebase_uid,
            email=body.email,
            display_name=body.display_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return UserResponse(user_id=user.firebase_uid, email=user.email, role=user.role)
