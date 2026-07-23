from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email : str
    password : str

def validate_signup_email(email : str):
    """
        Returns a boolean of whether email was correctly parsed,
        and returns and error code if any error is present.
    """

    err = None
    valid_email = True

    if "@" not in email:
        err = "Invalid email format, @ not present."
        valid_email = False

    

@router.post("/signup")
async def read_users(data : LoginRequest):
    email = data.email
    password = data.password

    print(email, password)

    return {
        "message" : "Recieved",
    }
