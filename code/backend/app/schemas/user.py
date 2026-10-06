from pydantic import BaseModel, EmailStr, field_validator

_MIN_PASSWORD_LENGTH = 8


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_must_meet_minimum_length(cls, v: str) -> str:
        if len(v) < _MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {_MIN_PASSWORD_LENGTH} characters long."
            )
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None

    @field_validator("password")
    @classmethod
    def password_must_meet_minimum_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) < _MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {_MIN_PASSWORD_LENGTH} characters long."
            )
        return v


class UserProfileUpdate(BaseModel):

    email: EmailStr | None = None
    password: str | None = None

    @field_validator("password")
    @classmethod
    def password_must_meet_minimum_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) < _MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {_MIN_PASSWORD_LENGTH} characters long."
            )
        return v


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    model_config = {"from_attributes": True}


class ProfileUpdateResponse(BaseModel):

    user: User
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    email: str | None = None
