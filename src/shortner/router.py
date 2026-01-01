from typing import Annotated

from fastapi import Body, APIRouter, status, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NoLongUrlFoundError, SlugAlreadyExistsError
from src.shortner.service import generate_short_url, get_url_by_slug
from src.database.db import get_session


shortner_router = APIRouter(tags=["contacts"])

@shortner_router.post("/short_url", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def generate_slug(
    long_url: Annotated[str, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        new_slug = await generate_short_url(long_url, session)
    except SlugAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Slug can not be generated",
        )
    return {"data": new_slug}


@shortner_router.get("/{slug}", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
async def redirect_to_url(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        long_url = await get_url_by_slug(slug, session)
    except NoLongUrlFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link doesn't exists")
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
