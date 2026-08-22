"""SKU mapping from diagram cell label/style."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Literal, Optional

from cost.config import SKU_MAP


@dataclass(frozen=True)
class MapCandidate:
    sku: str
    cloud: str
    category: str


@dataclass(frozen=True)
class MapResult:
    kind: Literal["unique", "none", "ambiguous"]
    candidate: Optional[MapCandidate] = None
    candidates: Optional[List[MapCandidate]] = None


_SPACE_RE = re.compile(r"[\s_\-]+")


def _normalize_label(label: str) -> str:
    """Casefold + collapse spaces/underscores/hyphens for A1 uppercase labels."""
    return _SPACE_RE.sub(" ", (label or "").casefold()).strip()


def _compact_label(label: str) -> str:
    """Normalized label with spaces removed (CLOUD RUN ↔ CLOUDRUN)."""
    return _normalize_label(label).replace(" ", "")


def _phrase(s: str) -> str:
    return f" {s} "


def _label_aliases(row: dict) -> List[str]:
    aliases: List[str] = []
    single = row.get("match_label", "")
    if isinstance(single, str) and single.strip():
        aliases.append(single)
    multi = row.get("match_labels", [])
    if isinstance(multi, list):
        aliases.extend(str(x) for x in multi if str(x).strip())
    return aliases


def _label_matches(label: str, aliases: List[str]) -> bool:
    """Match label to aliases case-insensitively.

    Rules (in order):
    - exact after normalize
    - exact after compact (spaces stripped) — CLOUDRUN ↔ Cloud Run
    - whole-phrase containment (word-boundary style) — avoids API⊂Apigee, LB⊂ALB
    """
    if not aliases:
        return False
    norm = _normalize_label(label)
    compact = _compact_label(label)
    if not norm:
        return False
    for alias in aliases:
        alias_n = _normalize_label(alias)
        alias_c = _compact_label(alias)
        if not alias_n:
            continue
        if norm == alias_n or compact == alias_c:
            return True
        # Alias as whole phrase inside label only（避免 SQL⊂Cloud SQL、LB⊂ALB）
        # e.g. alias "EC2" matches label "Amazon EC2 Instances"
        if _phrase(alias_n) in _phrase(norm):
            return True
    return False


def _row_matches(label: str, style: str, row: dict) -> bool:
    res_icon = row.get("match_res_icon", "")
    if res_icon:
        return res_icon in (style or "")

    aliases = _label_aliases(row)
    if not aliases:
        return False
    if not _label_matches(label, aliases):
        return False

    style_need = row.get("match_style_contains", "")
    # A1 產圖常用 shape=image（無 aws4／resIcon）；有指定 style 時才強制。
    if style_need and style_need not in (style or ""):
        return False
    return True


def map_cell(label: str, style: str) -> MapResult:
    hits: List[MapCandidate] = []
    seen: set[tuple[str, str]] = set()
    for row in SKU_MAP.get("mappings", []):
        if not _row_matches(label, style, row):
            continue
        key = (row["sku"], row["cloud"])
        if key in seen:
            continue
        seen.add(key)
        hits.append(
            MapCandidate(
                sku=row["sku"],
                cloud=row["cloud"],
                category=row.get("category", "other"),
            )
        )
    if not hits:
        return MapResult(kind="none")
    if len(hits) == 1:
        return MapResult(kind="unique", candidate=hits[0])
    return MapResult(kind="ambiguous", candidates=hits)
