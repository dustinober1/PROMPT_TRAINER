"""
Basic sanitization helpers to guard against script injection and empty strings.
"""

import re
from typing import Optional
from fastapi import HTTPException, status

FORBIDDEN_PATTERN = re.compile(r"<\s*script", re.IGNORECASE)


def sanitize_text(value: Optional[str], field: str, min_length: int = 1, max_length: int = 5000) -> Optional[str]:
    """
    Trim text, enforce length bounds, and reject obvious script tags.

    Returns the sanitized string or None if input was None.
    """
    if value is None:
        return None

    cleaned = value.strip()
    if len(cleaned) < min_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field} must be at least {min_length} characters.",
        )
    if len(cleaned) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field} must be at most {max_length} characters.",
        )
    if FORBIDDEN_PATTERN.search(cleaned):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field} contains disallowed content.",
        )
    return cleaned
