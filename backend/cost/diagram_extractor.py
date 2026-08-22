"""Extract priceable mxGraph cells from diagram XML (FR-1.1)."""

from __future__ import annotations

import html
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

from services.wa_rule_engine import sanitize_mxgraph_xml

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PriceableCell:
    mxcell_id: str
    label_plain: str
    style: str


_TAG_RE = re.compile(r"<[^>]+>")
_RES_ICON_RE = re.compile(r"resIcon=([^;]+)")


def _plain_label(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    text = _TAG_RE.sub("", text)
    return text.strip()


def _label_from_res_icon(style: str) -> str:
    match = _RES_ICON_RE.search(style or "")
    if not match:
        return ""
    slug = match.group(1).split(".")[-1]
    return slug.replace("_", " ").strip()


def _is_excluded_style(style: str) -> bool:
    s = style or ""
    lowered = s.lower()
    if "group" in lowered or "swimlane" in lowered:
        return True
    if "container=1" in lowered:
        return True
    return False


def _parse_root(xml_data: str) -> ET.Element:
    raw = xml_data or ""
    try:
        return ET.fromstring(raw)
    except ET.ParseError as first_err:
        cleaned = sanitize_mxgraph_xml(raw)
        if cleaned == raw:
            raise ValueError(f"invalid_mxgraph_xml: {first_err}") from first_err
        try:
            return ET.fromstring(cleaned)
        except ET.ParseError as second_err:
            raise ValueError(f"invalid_mxgraph_xml: {second_err}") from second_err


def extract_priceable_cells(xml_data: str) -> List[PriceableCell]:
    try:
        root = _parse_root(xml_data)
    except ValueError as exc:
        logger.warning("diagram XML unparseable for cost extract: %s", exc)
        return []

    cells: List[PriceableCell] = []
    for elem in root.iter("mxCell"):
        if elem.get("edge") == "1":
            continue
        if elem.get("vertex") != "1" and elem.get("edge") is not None:
            continue
        cell_id = elem.get("id")
        if not cell_id or cell_id == "0":
            continue
        style = elem.get("style") or ""
        if _is_excluded_style(style):
            continue
        label = _plain_label(elem.get("value"))
        if not label:
            label = _label_from_res_icon(style)
        if not label:
            continue
        cells.append(PriceableCell(mxcell_id=cell_id, label_plain=label, style=style))
    return cells
