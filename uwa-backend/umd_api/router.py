"""FastAPI routes for Testudo-backed course search."""

import logging

from fastapi import APIRouter, HTTPException, Query, status
from starlette.concurrency import run_in_threadpool

from .schemas import CourseResult
from .scraper import DEFAULT_SEMESTER, TestudoScraperError, search_courses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/courses", response_model=list[CourseResult])
async def get_courses(
    query: str = Query(
        ...,
        min_length=4,
        max_length=9,
        description="Partial Testudo course code, such as CMSC13.",
    ),
    semester: str = Query(
        DEFAULT_SEMESTER,
        pattern=r"^\d{6}$",
        description="Testudo term identifier in YYYYMM format.",
    ),
) -> list[CourseResult]:
    try:
        return await run_in_threadpool(search_courses, query, semester)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except TestudoScraperError as exc:
        logger.exception("Testudo course search failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Testudo is currently unavailable or returned unexpected data.",
        ) from exc
