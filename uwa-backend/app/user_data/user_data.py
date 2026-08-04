import logging

from fastapi import APIRouter, status
from app.schemas.user_data import SaveUserCourseInput
from fastapi.responses import JSONResponse


from app.db import Database

router = APIRouter()
logger = logging.getLogger(__name__)

database = Database()

def api_response(status_code: int, message: str) -> JSONResponse:
    """Return matching HTTP and JSON status values."""
    return JSONResponse(
        status_code=status_code,
        content={"status": status_code, "message": message},
    )

@router.post("/save_user_course")
async def save_user_course(data : SaveUserCourseInput) -> JSONResponse:
    user_id = data.user_id
    course = data.course
    section = data.section

    try:
        query = f"""
        INSERT INTO public.user_saved_courses (user_id, course, section)
        SELECT '{user_id}', '{course}', '{section}'
        WHERE NOT EXISTS (
            SELECT 1
            FROM public.user_saved_courses
            WHERE user_id = '{user_id}'
            AND course = '{course}'
            AND section = '{section}'
        )
        """

        await database.connect()
        await database.execute(query)
    except:
        logger.exception(
            f"Unable to insert values (user_id : {user_id}, course : {course} into public.user_saved_course)"
        )
        return api_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "User record saved!") 

    return api_response(status.HTTP_201_CREATED, "User record saved!")
    

