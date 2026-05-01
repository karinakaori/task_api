from typing import Annotated

from fastapi import Header


async def get_current_user_id(x_user_id: Annotated[str | None, Header()] = None) -> str | None:
    """Placeholder for future authentication without changing endpoint signatures later."""
    return x_user_id
