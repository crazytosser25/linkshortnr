import os
import secrets
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud import add_slug_to_database, get_long_url_by_slug_from_database, find_url
from src.exceptions import NoLongUrlFoundError, SlugAlreadyExistsError
from src.shortner.shortener import generate_random_slug


load_dotenv()
PASSCODE = os.getenv("PASSCODE")

async def generate_short_url(
        long_url: str,
        custom_slug: str | None,
        session: AsyncSession,
) -> str:
    async def _generate_slug_and_add_to_db() -> str:
        slug = custom_slug or generate_random_slug()
        await add_slug_to_database(
            slug, long_url, session
        )
        return slug
    double_slug = await find_url(long_url, session)
    if double_slug:
        return double_slug
    else:
        for attempt in range(5):
            try:
                slug = await _generate_slug_and_add_to_db()
                return slug
            except SlugAlreadyExistsError as ex:
                if attempt == 4:
                    raise SlugAlreadyExistsError from ex
        return slug

async def get_url_by_slug(slug: str, session: AsyncSession) -> str:
    long_url = await get_long_url_by_slug_from_database(slug, session)
    if not long_url:
        raise NoLongUrlFoundError()
    return long_url

def check_pwd(password: str) -> bool:
    return secrets.compare_digest(password, PASSCODE)
