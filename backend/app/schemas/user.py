from pydantic import BaseModel


class UserSync(BaseModel):
    firebase_uid: str
    email: str
    display_name: str | None = None


class UserResponse(BaseModel):
    user_id: str
    email: str
    role: str
