import logging
import re

from fastapi import APIRouter, HTTPException, status
from firebase_admin import auth as firebase_auth
from starlette.concurrency import run_in_threadpool

from app.db import Database
from app.fireauth import FireAuth
from app.schemas import SignUpRequest

router = APIRouter()
logger = logging.getLogger(__name__)


def validate_signup_password(password: str):
    """
        Returns a boolean of whether password was correctly parsed,
        and returns and error code if any error is present.
    """

    is_valid_password = True
    err = None

    if len(password) < 8:
        is_valid_password = False
        err = "Make sure your password is at least 8 characters"

    elif re.search("[0-9]", password) is None:
        is_valid_password = False
        err = "Make sure your password has a number in it"

    elif re.search("[A-Z]", password) is None:
        is_valid_password = False
        err = "Make sure your password has a capital letter in it"

    return is_valid_password, err

async def process_user_signup(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> str:
    """Create matching Firebase Auth and PostgreSQL user records."""

    is_valid_email = True
    err = None

    auth_client = FireAuth()

    try:
        user_record = await run_in_threadpool(
            auth_client.sign_up_user,
            email,
            password,
        )
    except firebase_auth.EmailAlreadyExistsError as exc:
        is_valid_email = False
        err = "An account with this email already exists."
    except ValueError as exc:
        is_valid_email = False
        err = "Firebase rejected the email address."

    if not is_valid_email:
        return is_valid_email, err

    database: Database | None = None

    try:
        database = Database()
        await database.connect()
        await database.execute(
            """
            INSERT INTO public.users (user_id, first_name, last_name, email)
            VALUES (%(user_id)s, %(first_name)s, %(last_name)s, %(email)s)
            """,
            {
                "user_id": user_record.uid,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            },
        )
    except Exception:
        try:
            await run_in_threadpool(auth_client.delete_user, user_record.uid)
        except Exception:
            logger.exception(
                "Could not roll back Firebase user %s after database failure",
                user_record.uid,
            )
        raise
    finally:
        if database is not None:
            await database.close()

    return is_valid_email, err
    

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up_user(data: SignUpRequest):
    """
     Signs up user in database, and make sures both Email and password are valid.
     Status Values:
        - 400 : Successfull signup
        - 401 : Invalid Email
        - 402 : Invalid Password
    """
    email = data.email.strip().lower()
    password = data.password
    first_name = data.firstName
    last_name = data.lastName

    # Apply the application's password policy before sending it to Firebase.
    is_valid_password, err = validate_signup_password(password)
    if not is_valid_password:
        return {
            "message" : 402,
            "err" : err,
        }

    is_valid_email, err = await process_user_signup(email, password, first_name, last_name)

    if not is_valid_email:
        return {
            "message" : 401,
            "err" : err,
        }

    return {
        "message": "User successfully created",
        "status": 400,
    }
