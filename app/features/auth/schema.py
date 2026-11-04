from pydantic import BaseModel


class UserLoginResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserLoginResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    access_token: str
    refresh_token: str
