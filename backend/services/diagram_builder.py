"""
diagram_builder.py — A1 架構圖組裝模組

職責：
  將 LLM tool 回傳的 groups / nodes / edges（絕對座標）轉成 draw.io mxGraphModel XML。
  節點圖示透過 n8n webhook 取得 SVG；失敗時使用灰底 fallback。

注意：
  - 本模組不含 LLM 呼叫，僅負責幾何巢狀與 XML 字串組裝。
  - 行為需與重構前 agent_router 內嵌邏輯一致。
"""

from __future__ import annotations

import base64
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# 進度回呼：用於 SSE progress（例如「正在取得 EC2 圖示」）
ProgressCallback = Callable[[str], Awaitable[None]]

# draw.io AWS 群組樣式（與重構前相同）
GROUP_STYLES = {
    "aws_cloud": (
        "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;"
        "strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;"
        "spacingLeft=30;fontColor=#232F3E;dashed=0;"
    ),
    "vpc": (
        "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;"
        "strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;"
        "spacingLeft=30;fontColor=#AAB7B8;dashed=0;"
    ),
    "az": (
        "fillColor=none;strokeColor=#147EBA;dashed=1;verticalAlign=top;"
        "fontStyle=0;fontColor=#147EBA;whiteSpace=wrap;html=1;"
    ),
    "public_subnet": (
        "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;"
        "strokeColor=#7AA116;fillColor=#F2F6E8;verticalAlign=top;align=left;"
        "spacingLeft=30;fontColor=#248814;dashed=0;"
    ),
    "private_subnet": (
        "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;"
        "strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;"
        "spacingLeft=30;fontColor=#147EBA;dashed=0;"
    ),
    "gcp_cloud": (
        "shape=mxgraph.aws4.group;strokeColor=#4285F4;fillColor=none;verticalAlign=top;align=left;"
        "spacingLeft=30;fontColor=#4285F4;dashed=0;"
    ),
    "gcp_vpc": (
        "shape=mxgraph.aws4.group;strokeColor=#34A853;fillColor=none;verticalAlign=top;align=left;"
        "spacingLeft=30;fontColor=#34A853;dashed=0;"
    ),
    "gcp_subnet": (
        "shape=mxgraph.aws4.group;strokeColor=#FBBC05;fillColor=#FFFDF0;verticalAlign=top;align=left;"
        "spacingLeft=30;fontColor=#FBBC05;dashed=0;"
    ),
}


def is_inside(child: dict[str, Any], parent: dict[str, Any]) -> bool:
    """判斷 child 的邊界盒是否完全落在 parent 內（節點預設 80x80）。"""
    cw = child.get("width", 80)
    ch = child.get("height", 80)
    return (
        child["x"] >= parent["x"]
        and child["y"] >= parent["y"]
        and child["x"] + cw <= parent["x"] + parent.get("width", 0)
        and child["y"] + ch <= parent["y"] + parent.get("height", 0)
    )


async def fetch_icon_from_n8n(service_name: str, provider: str = "AWS") -> str:
    """
    向 n8n webhook 取得服務 SVG。
    若未設定 N8N_WEBHOOK_URL 或請求失敗，回傳灰底文字 fallback SVG。
    """
    webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    fallback_svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        f'<rect width="100" height="100" fill="#cccccc"/>'
        f'<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" '
        f'fill="black" font-size="14">{service_name}</text></svg>'
    )

    if not webhook_url:
        return fallback_svg

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url, json={"service": service_name, "provider": provider}, timeout=5.0
            )
            if response.status_code != 200:
                return fallback_svg

            content = response.text.strip()
            if content.startswith("<svg"):
                return content

            try:
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    for item in data:
                        name = item.get(
                            "name", item.get("icon_name", item.get("service", ""))
                        )
                        if service_name.lower() in name.lower() or name.lower() in service_name.lower():
                            if "svg_content" in item:
                                    return item["svg_content"]
                            if "svg" in item:
                                return item["svg"]

                    item = data[0]
                    if "svg_content" in item:
                        return item["svg_content"]
                    if "svg" in item:
                        return item["svg"]

                elif isinstance(data, dict):
                    if "svg_content" in data:
                        return data["svg_content"]
                    if "svg" in data:
                        return data["svg"]
                    if "data" in data and "svg" in data["data"]:
                        return data["data"]["svg"]

            except Exception as e:
                logger.warning("解析 n8n 回應失敗: %s", e)
    except Exception as e:
        logger.warning("向 n8n 取得 %s 圖示（供應商：%s）失敗: %s", service_name, provider, e)

    return fallback_svg


async def build_mxgraph_xml(
    groups: list[dict[str, Any]] | None,
    nodes: list[dict[str, Any]] | None,
    edges: list[dict[str, Any]] | None,
    on_progress: ProgressCallback | None = None,
    provider: str | None = None,
) -> str:
    """
    將 groups/nodes/edges 組裝為 mxGraphModel XML 字串。

    流程：
      1. 依面積排序 groups，用 is_inside 推算 parent 與相對座標
      2. 為 nodes 找最小包覆 group
      3. 輸出 group / node（含 n8n icon）/ orthogonal edge cells
    """
    groups = list(groups or [])
    nodes = list(nodes or [])
    edges = list(edges or [])

    if not provider:
        # 根據群組的類型自動偵測雲端平台供應商
        g_types = {g.get("type") for g in groups if g}
        if any(t in ("gcp_cloud", "gcp_vpc", "gcp_subnet") for t in g_types):
            provider = "GCP"
        else:
            provider = "AWS"

    if not nodes and not groups:
        raise ValueError("groups 與 nodes 皆為空，無法產圖")

    cells: list[str] = []

    # --- 巢狀：group 面積由大到小 ---
    for g in groups:
        g["area"] = g.get("width", 0) * g.get("height", 0)
    groups_sorted = sorted(groups, key=lambda x: x["area"], reverse=True)

    for g in groups_sorted:
        parent_id = "1"
        rel_x, rel_y = g["x"], g["y"]
        for potential_parent in groups_sorted:
            if g["id"] != potential_parent["id"] and potential_parent["area"] > g["area"]:
                if is_inside(g, potential_parent):
                    parent_id = potential_parent["id"]
                    rel_x = g["x"] - potential_parent["x"]
                    rel_y = g["y"] - potential_parent["y"]
        g["parent_id"] = parent_id
        g["rel_x"] = rel_x
        g["rel_y"] = rel_y

    for node in nodes:
        parent_id = "1"
        rel_x, rel_y = node["x"], node["y"]
        node["width"] = 80
        node["height"] = 80

        best_group = None
        for g in groups_sorted:
            if is_inside(node, g):
                best_group = g
        if best_group:
            parent_id = best_group["id"]
            rel_x = node["x"] - best_group["x"]
            rel_y = node["y"] - best_group["y"]

        node["parent_id"] = parent_id
        node["rel_x"] = rel_x
        node["rel_y"] = rel_y

    # --- Groups ---
    for g in groups_sorted:
        gid = g["id"]
        gname = g.get("name", "")
        gtype = g.get("type", "vpc")
        style = GROUP_STYLES.get(gtype, GROUP_STYLES["vpc"])
        w, h = g.get("width", 200), g.get("height", 200)
        pid = g["parent_id"]
        rx, ry = g["rel_x"], g["rel_y"]
        cells.append(
            f'<mxCell id="{gid}" value="{gname}" style="{style}" vertex="1" parent="{pid}">'
            f'<mxGeometry x="{rx}" y="{ry}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )

    # --- Nodes + n8n icons ---
    for idx, node in enumerate(nodes):
        node_id = node.get("id", f"node_{idx}")
        comp = node.get("name", "Unknown")
        pid = node["parent_id"]
        rx, ry = node["rel_x"], node["rel_y"]

        if on_progress:
            await on_progress(
                f"🔄 正在取得 {comp.upper()} 圖示 ({idx + 1}/{len(nodes)})..."
            )

        svg_content = await fetch_icon_from_n8n(comp, provider=provider)
        b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        style = (
            f"shape=image;image=data:image/svg+xml,{b64_svg};"
            "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
        )
        cells.append(
            f'<mxCell id="{node_id}" value="{comp.upper()}" style="{style}" vertex="1" parent="{pid}">'
            f'<mxGeometry x="{rx}" y="{ry}" width="80" height="80" as="geometry"/></mxCell>'
        )

    # --- Edges（直角連線）---
    for idx, edge in enumerate(edges):
        src = edge.get("source")
        tgt = edge.get("target")
        if src and tgt:
            edge_id = f"edge_{idx}"
            edge_style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;"
                "jettySize=auto;html=1;"
            )
            cells.append(
                f'<mxCell id="{edge_id}" edge="1" parent="1" source="{src}" target="{tgt}" '
                f'style="{edge_style}"><mxGeometry relative="1" as="geometry"/></mxCell>'
            )

    inner_xml = "".join(cells)
    return (
        f"<mxGraphModel><root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/>"
        f"{inner_xml}</root></mxGraphModel>"
    )
