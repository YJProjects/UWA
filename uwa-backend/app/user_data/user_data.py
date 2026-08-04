import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.schemas.user_data import SaveUserCourseInput
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.db import Database
from app.fireauth import FireAuth

router = APIRouter()
logger = logging.getLogger(__name__)

def api_response(status_code: int, message: str) -> JSONResponse:
    """Return matching HTTP and JSON status values."""
    return JSONResponse(
        status_code=status_code,
        content={"status": status_code, "message": message},
    )

async def authenticated_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """Return the UID from a valid Firebase bearer token."""
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A Firebase ID token is required.",
        )

    try:
        claims = await run_in_threadpool(FireAuth().verify_id_token, token)
        user_id = claims.get("uid") or claims.get("sub")
        if not user_id:
            raise ValueError("Firebase token does not contain a user ID")
        return str(user_id)
    except HTTPException:
        raise
    except Exception as error:
        logger.info("Firebase ID token verification failed: %s", error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The Firebase ID token is invalid or expired.",
        ) from error


@router.post("/save_user_course", status_code=status.HTTP_201_CREATED)
async def save_user_course(
    data: SaveUserCourseInput,
    user_id: Annotated[str, Depends(authenticated_user_id)],
) -> JSONResponse:
    course = data.course.strip().upper()
    section = data.section.strip()
    database: Database | None = None

    try:
        database = Database()
        await database.connect()
        await database.execute(
            """
            INSERT INTO public.user_saved_courses (user_id, course, section)
            VALUES (%(user_id)s, %(course)s, %(section)s)
            ON CONFLICT (user_id, course, section) DO NOTHING
            """,
            {
                "user_id": user_id,
                "course": course,
                "section": section,
            },
        )
    except Exception:
        logger.exception(
            "Unable to save course %s section %s for user %s",
            course,
            section,
            user_id,
        )
        return api_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Unable to save the course. Please try again.",
        )
    finally:
        if database is not None:
            try:
                await database.close()
            except Exception:
                logger.exception("Could not close the saved-course database pool")

    return api_response(status.HTTP_201_CREATED, "User record saved!")
