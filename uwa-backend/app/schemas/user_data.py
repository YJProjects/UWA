from pydantic import BaseModel

class SaveUserCourseInput(BaseModel):
    user_id : str
    course : str
    section : str