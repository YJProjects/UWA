import logging
import re

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from firebase_admin import auth as firebase_auth
from starlette.concurrency import run_in_threadpool

from app.db import Database
from app.fireauth import FireAuth
from app.schemas import SignUpRequest, LoginRequest

from app.config import BOT_EMAIL, BOT_EMAIL_APP_PASSWORD

import smtplib
from email.message import EmailMessage

router = APIRouter()
logger = logging.getLogger(__name__)


class SignupPersistenceError(Exception):
    """Database persistence failed after Firebase user creation was rolled back."""

class EmailVerificationLinkSendError(Exception):
    """Unable to send verification email to user."""

class SignupRollbackError(Exception):
    """Both database persistence and the compensating Firebase deletion failed."""

def send_verification_email(receiver_email : str, link : str):
    sender_email = BOT_EMAIL
    receiver_email = receiver_email

    message = EmailMessage()

    message["Subject"] = "Verify Your Account"
    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content("Thank you for signing up for the unofficial umd waitlist app. \n Click the following link to verify. \n" + link)

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465 
    SENDER_EMAIL = sender_email
    SENDER_PASSWORD = BOT_EMAIL_APP_PASSWORD

    try:
        # Establish a secure SSL connection
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
    except Exception as e:
        print(f"Failed to send email: {e}")


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
) -> tuple[bool, str | None, int | None]:
    """Create matching Firebase Auth and PostgreSQL user records."""

    auth_client = FireAuth()

    try:
        user_record = await run_in_threadpool(
            auth_client.sign_up_user,
            email,
            password,
        )
        
    except firebase_auth.EmailAlreadyExistsError:
        return False, "An account with this email already exists.", status.HTTP_409_CONFLICT
    except ValueError:
        return False, "Firebase rejected the email address.", status.HTTP_400_BAD_REQUEST

    try:
        url = auth_client.generate_verification_link(email)
        send_verification_email(email, url)

    except Exception as signup_error:
        logger.exception(
            "Could not send verification email to : %s",
            email,
        )

        await run_in_threadpool(auth_client.delete_user, user_record.uid)

        raise EmailVerificationLinkSendError(
            "Unable to send verification email to user"
        ) from signup_error



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
    except Exception as database_error:
        try:
            await run_in_threadpool(auth_client.delete_user, user_record.uid)
        except Exception as rollback_error:
            logger.exception(
                "Could not roll back Firebase user %s after database failure",
                user_record.uid,
            )
            raise SignupRollbackError(
                "User persistence and Firebase rollback both failed"
            ) from rollback_error

        logger.info(
            "Rolled back Firebase user %s after database failure",
            user_record.uid,
        )
        raise SignupPersistenceError(
            "Database persistence failed; Firebase user was rolled back"
        ) from database_error
    finally:
        if database is not None:
            try:
                await database.close()
            except Exception:
                # A cleanup failure must not turn an already-committed signup
                # into a reported failure that leaves the two stores inconsistent.
                logger.exception("Could not close the database pool after signup")

    return True, None, None


def api_response(status_code: int, message: str) -> JSONResponse:
    """Return matching HTTP and JSON status values."""
    return JSONResponse(
        status_code=status_code,
        content={"status": status_code, "message": message},
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up_user(data: SignUpRequest):
    """
     Signs up user in database, and make sures both Email and password are valid.
     Status values:
        - 201: Successful signup
        - 400: Invalid email or password
        - 409: Email already exists
      """
    email = data.email.strip().lower()
    password = data.password
    first_name = data.firstName
    last_name = data.lastName

    # Apply the application's password policy before sending it to Firebase.
    is_valid_password, err = validate_signup_password(password)
    if not is_valid_password:
        return api_response(status.HTTP_400_BAD_REQUEST, err)

    try:
        is_valid_email, err, error_status = await process_user_signup(
            email,
            password,
            first_name,
            last_name,
        )
    except SignupRollbackError:
        logger.exception("Signup failed and Firebase rollback was unsuccessful")
        return api_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Signup failed and automatic account rollback was unsuccessful.",
        )
    except SignupPersistenceError:
        logger.exception("Signup persistence failed after Firebase rollback")
        return api_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Signup failed. The Firebase account was rolled back; please try again.",
        )
    except EmailVerificationLinkSendError:
        return api_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Unable to send user verification email.",
        )

    if not is_valid_email:
        assert error_status is not None and err is not None
        return api_response(error_status, err)

    return api_response(status.HTTP_201_CREATED, "User successfully created")
