from pydantic import BaseModel, Field


class UserMiniResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
