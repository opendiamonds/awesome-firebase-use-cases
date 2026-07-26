"""
lens_router.py — A3 Lens criteria editor API (requires A3.review).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import User
from services.lens_service import (
    make_question_template,
    resolve_active_lens,
    save_active_lens,
    suggest_improvement_plan,
    validate_lens,
)
from services.rbac import require_story_action

router = APIRouter()


class SuggestImprovementBody(BaseModel):
    title: str = Field(..., min_length=1)


class PutLensBody(BaseModel):
    lens: dict[str, Any]


@router.get("/lens/active")
def get_active_lens(
    current_user: User = Depends(require_story_action("A3", "review")),
    db: Session = Depends(get_db),
):
    lens = resolve_active_lens(db)
    return {
        "source": "database" if _has_db_row(db) else "file",
        "lens": lens,
        "updated_by": current_user.id,
    }


def _has_db_row(db: Session) -> bool:
    from services.lens_service import get_active_lens_row

    return get_active_lens_row(db) is not None


@router.put("/lens/active")
def put_active_lens(
    body: PutLensBody,
    current_user: User = Depends(require_story_action("A3", "review")),
    db: Session = Depends(get_db),
):
    try:
        saved = save_active_lens(db, body.lens, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"ok": True, "source": "database", "lens": saved}


@router.get("/lens/new-question-template")
def new_question_template(
    pillar_id: str = Query(...),
    title: str = Query("New review question"),
    current_user: User = Depends(require_story_action("A3", "review")),
):
    _ = current_user
    try:
        return {"question": make_question_template(pillar_id, title)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/lens/suggest-improvement-plan")
def post_suggest_improvement(
    body: SuggestImprovementBody,
    current_user: User = Depends(require_story_action("A3", "review")),
):
    _ = current_user
    return {"displayText": suggest_improvement_plan(body.title)}


@router.post("/lens/validate")
def post_validate_lens(
    body: PutLensBody,
    current_user: User = Depends(require_story_action("A3", "review")),
):
    _ = current_user
    try:
        validate_lens(body.lens)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"ok": True}
