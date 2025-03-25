# app/schemas/user.py
from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    username: str
    name: str

    class Config:
        from_attributes = True