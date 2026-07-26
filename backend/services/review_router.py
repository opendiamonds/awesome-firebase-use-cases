"""
review_router.py — A3 Well-Architected reviews API（SSE + JSON）
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import ArchitectureReview, User
from services.rbac import require_story_action
from services.review_orchestrator import (
    audit_log,
    get_accessible_diagram,
    retry_suggestions,
    review_to_dict,
    start_review,
)

logger = logging.getLogger("cloud360.review_router")

router = APIRouter()


class StartReviewBody(BaseModel):
    diagram_id: int
    provider: str = "aws"
    replace_latest: bool = False


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _sse_response(generator) -> StreamingResponse:
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/reviews")
async def create_review(
    body: StartReviewBody,
    current_user: User = Depends(require_story_action("A3", "edit")),
    db: Session = Depends(get_db),
):
    diagram = get_accessible_diagram(db, current_user, body.diagram_id)
    if not diagram:
        raise HTTPException(status_code=403, detail="無法存取此架構圖或不存在")

    async def event_generator():
        async for event in start_review(
            db,
            current_user,
            diagram,
            provider=(body.provider or "aws").lower(),
            replace_latest=body.replace_latest,
        ):
            yield _sse(event)

    return _sse_response(event_generator())


@router.get("/reviews")
def list_reviews(
    diagram_id: Optional[int] = Query(None),
    include_archived: bool = Query(False),
    current_user: User = Depends(require_story_action("A3", "view")),
    db: Session = Depends(get_db),
):
    if diagram_id is None:
        raise HTTPException(status_code=400, detail="diagram_id 必填")
    diagram = get_accessible_diagram(db, current_user, diagram_id)
    if not diagram:
        raise HTTPException(status_code=403, detail="無法存取此架構圖或不存在")

    q = db.query(ArchitectureReview).filter(
        ArchitectureReview.diagram_id == diagram_id
    )
    if not include_archived:
        q = q.filter(ArchitectureReview.archived.is_(False))
    rows = q.order_by(ArchitectureReview.created_at.desc()).all()
    audit_log(
        "review_list",
        user_id=current_user.id,
        diagram_id=diagram_id,
    )
    return [review_to_dict(r) for r in rows]


@router.get("/reviews/{review_id}")
def get_review(
    review_id: int,
    current_user: User = Depends(require_story_action("A3", "view")),
    db: Session = Depends(get_db),
):
    row = db.query(ArchitectureReview).filter(ArchitectureReview.id == review_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="評核不存在")
    diagram = get_accessible_diagram(db, current_user, row.diagram_id)
    if not diagram:
        raise HTTPException(status_code=403, detail="無法存取此評核")
    audit_log(
        "review_get",
        user_id=current_user.id,
        review_id=row.id,
        diagram_id=row.diagram_id,
    )
    return review_to_dict(row)


@router.post("/reviews/{review_id}/retry-suggestions")
async def retry_review_suggestions(
    review_id: int,
    current_user: User = Depends(require_story_action("A3", "edit")),
    db: Session = Depends(get_db),
):
    row = db.query(ArchitectureReview).filter(ArchitectureReview.id == review_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="評核不存在")
    diagram = get_accessible_diagram(db, current_user, row.diagram_id)
    if not diagram:
        raise HTTPException(status_code=403, detail="無法存取此架構圖")

    async def event_generator():
        async for event in retry_suggestions(db, current_user, row, diagram):
            yield _sse(event)

    return _sse_response(event_generator())
