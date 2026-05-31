from pydantic import BaseModel, Field


class TokenOut(BaseModel):

    access_token: str

    token_type: str = "bearer"

    expires_in: int





class LoginIn(BaseModel):

    username: str

    password: str

    captcha_id: str

    captcha_code: str





class CaptchaOut(BaseModel):

    captcha_id: str

    question: str





class ChangePasswordIn(BaseModel):

    current_password: str = Field(min_length=1, max_length=128)

    new_password: str = Field(min_length=8, max_length=128)


