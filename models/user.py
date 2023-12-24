from typing import Dict, List

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr


user=User(id=1,name='azim',age=34,email='azim@gmail.com')
print(user)

# class UserResponseModel(BaseModel):
#     statuscode: int
#     message: str
#     payload: Dict[str, List[User]]
