"""
lens_service.py — A3 Offline Custom Lens CRUD / validation (requires A3.review).
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Optional

from sqlalchemy.orm import Session

from models import User, WaLens
from services.wa_lens_engine import LENS_ID, load_lens

logger = logging.getLogger("cloud360.lens_service")

REQUIRED_PILLAR_IDS = frozenset(
    {
        "security",
        "reliability",
        "cost_optimization",
        "performance_efficiency",
        "operational_excellence",
    }
)


def suggest_improvement_plan(title: str) -> str:
    t = (title or "").strip() or "this criterion"
    return (
        f"Review the architecture against: {t}. "
        "Add or label the missing controls on the diagram, then re-run the assessment."
    )


def make_question_template(
    pillar_id: str, title: str = "New review question"
) -> dict[str, Any]:
    if pillar_id not in REQUIRED_PILLAR_IDS:
        raise ValueError(f"Unknown pillar_id: {pillar_id}")
    prefix = pillar_id[:3]
    qid = f"{prefix}_{uuid.uuid4().hex[:8]}"
    choice_id = f"{qid}_ok"
    return {
        "id": qid,
        "title": title,
        "description": "",
        "choices": [
            {
                "id": choice_id,
                "title": "Criterion is satisfied on the diagram",
                "improvementPlan": {"displayText": suggest_improvement_plan(title)},
            }
        ],
        "riskRules": [
            {"condition": choice_id, "risk": "NO_RISK"},
            {"condition": "default", "risk": "MEDIUM_RISK"},
        ],
    }


def validate_lens(lens: dict[str, Any]) -> None:
    if not isinstance(lens, dict):
        raise ValueError("Lens must be a JSON object")
    if lens.get("schemaVersion") != "2021-11-01":
        raise ValueError("schemaVersion must be 2021-11-01")
    pillars = lens.get("pillars")
    if not isinstance(pillars, list):
        raise ValueError("pillars must be a list")
    ids = [p.get("id") for p in pillars if isinstance(p, dict)]
    if set(ids) != REQUIRED_PILLAR_IDS:
        raise ValueError(
            "pillars must be exactly the five fixed ids "
            f"(got {sorted(ids)})"
        )
    if len(ids) != len(REQUIRED_PILLAR_IDS):
        raise ValueError("Duplicate or missing pillars")
    for p in pillars:
        qs = p.get("questions") or []
        if not isinstance(qs, list) or len(qs) < 1:
            raise ValueError(f"Pillar {p.get('id')} must have at least 1 question")
        for q in qs:
            if not q.get("id"):
                raise ValueError("Each question needs an id")
            if not isinstance(q.get("choices"), list) or not q["choices"]:
                raise ValueError(f"Question {q.get('id')} needs choices")
            if not isinstance(q.get("riskRules"), list) or not q["riskRules"]:
                raise ValueError(f"Question {q.get('id')} needs riskRules")


def _index_questions(lens: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in lens.get("pillars") or []:
        for q in p.get("questions") or []:
            qid = q.get("id")
            if qid:
                out[str(qid)] = q
    return out


def preserve_existing_risk_rules(
    incoming: dict[str, Any], previous: dict[str, Any]
) -> dict[str, Any]:
    """For existing question ids, keep previous riskRules (and id) — UI must not edit them."""
    prev_q = _index_questions(previous)
    for p in incoming.get("pillars") or []:
        for q in p.get("questions") or []:
            qid = q.get("id")
            if qid and qid in prev_q:
                q["id"] = prev_q[qid]["id"]
                q["riskRules"] = prev_q[qid].get("riskRules") or q.get("riskRules")
    return incoming


def get_active_lens_row(db: Session) -> Optional[WaLens]:
    return (
        db.query(WaLens)
        .filter(WaLens.is_active.is_(True), WaLens.lens_id == LENS_ID)
        .order_by(WaLens.id.desc())
        .first()
    )


def resolve_active_lens(db: Optional[Session] = None) -> dict[str, Any]:
    if db is not None:
        row = get_active_lens_row(db)
        if row and row.body_json:
            try:
                return json.loads(row.body_json)
            except json.JSONDecodeError:
                logger.warning("wa_lenses body_json invalid; falling back to file")
    return load_lens()


def save_active_lens(
    db: Session, lens: dict[str, Any], user: User
) -> dict[str, Any]:
    previous = resolve_active_lens(db)
    merged = preserve_existing_risk_rules(lens, previous)
    validate_lens(merged)
    body = json.dumps(merged, ensure_ascii=False)

    # Deactivate other actives for this lens_id
    for row in (
        db.query(WaLens)
        .filter(WaLens.lens_id == LENS_ID, WaLens.is_active.is_(True))
        .all()
    ):
        row.is_active = False

    active = WaLens(
        lens_id=LENS_ID,
        is_active=True,
        body_json=body,
        updated_by=user.id,
    )
    db.add(active)
    db.commit()
    db.refresh(active)
    return merged
