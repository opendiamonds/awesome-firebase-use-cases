import os
import json
import base64
import urllib.parse
import httpx
import logging
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from services.auth import get_current_user
from models import User

# 設置日誌記錄器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

async def fetch_icon_from_n8n(service_name: str) -> str:
    webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    fallback_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#cccccc"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="black" font-size="14">{service_name}</text></svg>'''
    
    if not webhook_url:
        return fallback_svg
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json={"service": service_name}, timeout=5.0)
            if response.status_code == 200:
                content = response.text.strip()
                if content.startswith("<svg"):
                    return content
                try:
                    data = response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        for item in data:
                            name = item.get("name", item.get("icon_name", item.get("service", "")))
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
                    print(f"Error parsing n8n response: {str(e)}")
    except Exception as e:
        print(f"Failed to fetch icon for {service_name} from n8n: {e}")
        
    return fallback_svg

def is_inside(child, parent):
    # child and parent are dicts with x, y, width, height (for groups)
    # nodes are 80x80 defaults
    cw = child.get("width", 80)
    ch = child.get("height", 80)
    return (
        child["x"] >= parent["x"] and
        child["y"] >= parent["y"] and
        child["x"] + cw <= parent["x"] + parent.get("width", 0) and
        child["y"] + ch <= parent["y"] + parent.get("height", 0)
    )

@router.post("/generate")
async def chat_and_generate(request: ChatRequest, current_user: User = Depends(get_current_user)):
    messages = request.messages
    if not messages:
        raise HTTPException(status_code=400, detail="對話不可為空")
        
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    logger.info("========================================")
    logger.info("收到畫圖/對話請求，正在進行環境變數檢查...")
    logger.info(f"OPENROUTER_API_KEY 狀態: {'已設定' if openrouter_key else '未設定'}")
    logger.info(f"ANTHROPIC_API_KEY 狀態: {'已設定' if anthropic_key else '未設定'}")
    
    if not openrouter_key and not anthropic_key:
        logger.error("錯誤: 未設定 API Key")
        raise HTTPException(status_code=500, detail="尚未設定 OPENROUTER_API_KEY 或 ANTHROPIC_API_KEY 環境變數")

    system_prompt = """
    你是一位資深的 AWS 雲端架構師。你的任務是與使用者對話並釐清他們的雲端架構需求。
    請仔細閱讀對話歷史，判斷需求是否足夠明確。
    當需求明確時，請主動呼叫 `draw_architecture_diagram` 工具來為使用者產生架構圖。
    
    【繪圖指南：框架與座標】
    我們現在支援高級的「框架 (Groups)」！所有的節點與框架請給出「絕對座標 (Absolute X, Y)」，系統會自動處理巢狀結構。
    節點預設寬高為 80x80。框架請務必設定合適的 width 與 height 把它們包起來，**且平行層級的框架絕對不可重疊！**
    
    框架類型 (type) 包含: `aws_cloud`, `vpc`, `az`, `public_subnet`, `private_subnet`。
    【重要排版規範 - 請嚴格遵守座標範例以避免重疊】
    1. **AWS Cloud**: 最外層，包住所有東西。
       - 建議座標: x=0, y=0, width=1200, height=1000。
       - 邊緣服務 (Route53, WAF, CloudFront) 放在 AWS Cloud 內、VPC 上方 (y=50~150)。
    2. **VPC**: 放在 AWS Cloud 內部。
       - 建議座標: x=40, y=200, width=1100, height=750。
    3. **Availability Zone (AZ)**: **AZ 之間必須左右並排，絕對不可重疊！**
       - AZ 1 建議座標: x=80, y=250, width=480, height=650。
       - AZ 2 建議座標: x=600, y=250, width=480, height=650。
    4. **Subnets (Public/Private)**: 在 AZ 內建立。**同一個 AZ 內的 Subnets 請上下排列，絕對不可重疊！**
       - 若架構包含 App (EC2) 與 DB (RDS)，請將它們放在「不同」的 Private Subnet 中 (例如 App Subnet 與 Data Subnet)。
       - AZ 1 (x=80) 範例:
         - Public Subnet (放 ALB/NAT): x=100, y=300, width=440, height=150
         - App Private Subnet (放 EC2): x=100, y=470, width=440, height=200
         - Data Private Subnet (放 DB/RDS): x=100, y=690, width=440, height=180
       - AZ 2 (x=600) 範例:
         - Public Subnet: x=620, y=300, width=440, height=150
         - App Private Subnet: x=620, y=470, width=440, height=200
         - Data Private Subnet: x=620, y=690, width=440, height=180
       
    請務必保證座標空間足夠，並確保被包覆的節點絕對座標落在父框架的範圍內，且平行的框架(如 AZ與AZ、Subnet與Subnet)不可互相交疊！
    """
    
    model_name = os.environ.get("LLM_MODEL", "anthropic/claude-sonnet-4.6")
    
    formatted_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        formatted_messages.append({"role": msg.role, "content": msg.content})
        
    async def event_generator():
        tool_args_str = ""
        has_tool_call = False
        message_replied = False
        
        try:
            async with httpx.AsyncClient() as http_client:
                async with http_client.stream(
                    "POST",
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_name,
                        "messages": formatted_messages,
                        "temperature": 0.2,
                        "stream": True,
                        "tools": [
                            {
                                "type": "function",
                                "function": {
                                    "name": "draw_architecture_diagram",
                                    "description": "當架構需求釐清後，呼叫此工具來產生雲端架構圖。",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "groups": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "name": {"type": "string", "description": "例如 VPC, AZ-1, Public Subnet 1"},
                                                        "type": {"type": "string", "enum": ["aws_cloud", "vpc", "az", "public_subnet", "private_subnet"]},
                                                        "x": {"type": "integer", "description": "絕對 X 座標"},
                                                        "y": {"type": "integer", "description": "絕對 Y 座標"},
                                                        "width": {"type": "integer"},
                                                        "height": {"type": "integer"}
                                                    },
                                                    "required": ["id", "name", "type", "x", "y", "width", "height"]
                                                },
                                                "description": "架構圖上的框架/區域"
                                            },
                                            "nodes": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string", "description": "節點唯一識別碼"},
                                                        "name": {"type": "string", "description": "AWS 元件名稱，例如 waf, alb, ec2"},
                                                        "x": {"type": "integer", "description": "絕對 X 座標"},
                                                        "y": {"type": "integer", "description": "絕對 Y 座標"}
                                                    },
                                                    "required": ["id", "name", "x", "y"]
                                                },
                                                "description": "要畫在圖表上的 AWS 元件節點陣列"
                                            },
                                            "edges": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "source": {"type": "string", "description": "起始節點/群組的 ID"},
                                                        "target": {"type": "string", "description": "目標節點/群組的 ID"}
                                                    },
                                                    "required": ["source", "target"]
                                                },
                                                "description": "節點間的連線陣列"
                                            }
                                        },
                                        "required": ["nodes"]
                                    }
                                }
                            }
                        ]
                    },
                    timeout=60.0
                ) as resp:
                    if resp.status_code != 200:
                        error_text = await resp.aread()
                        error_msg = f"API Error: {resp.status_code}"
                        chunk = json.dumps({"type": "error", "content": error_msg})
                        yield f"data: {chunk}\n\n"
                        return
                    
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                            
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            
                            content = delta.get("content")
                            if content:
                                message_replied = True
                                chunk = json.dumps({"type": "message", "content": content})
                                yield f"data: {chunk}\n\n"
                                
                            tool_calls = delta.get("tool_calls")
                            if tool_calls:
                                for tc in tool_calls:
                                    if tc.get("function") and tc["function"].get("name") == "draw_architecture_diagram":
                                        if not has_tool_call:
                                            has_tool_call = True
                                            chunk = json.dumps({"type": "progress", "content": "🧠 正在規劃進階架構拓樸..."})
                                            yield f"data: {chunk}\n\n"
                                    if tc.get("function") and "arguments" in tc["function"]:
                                        tool_args_str += tc["function"]["arguments"]
                        except json.JSONDecodeError:
                            continue
                            
            if has_tool_call and tool_args_str:
                if not message_replied:
                    chunk = json.dumps({"type": "message", "content": "我已經為您產生了具備區域框架的架構圖，請參考右側畫面！"})
                    yield f"data: {chunk}\n\n"
                
                try:
                    args = json.loads(tool_args_str)
                    groups = args.get("groups", [])
                    nodes = args.get("nodes", [])
                    edges = args.get("edges", [])
                    
                    if nodes or groups:
                        cells = []
                        
                        # 定義樣式
                        styles = {
                            "aws_cloud": "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#232F3E;dashed=0;",
                            "vpc": "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;",
                            "az": "fillColor=none;strokeColor=#147EBA;dashed=1;verticalAlign=top;fontStyle=0;fontColor=#147EBA;whiteSpace=wrap;html=1;",
                            "public_subnet": "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#7AA116;fillColor=#F2F6E8;verticalAlign=top;align=left;spacingLeft=30;fontColor=#248814;dashed=0;",
                            "private_subnet": "shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#00A4A6;fillColor=#E6F6F7;verticalAlign=top;align=left;spacingLeft=30;fontColor=#147EBA;dashed=0;"
                        }
                        
                        # 找出巢狀關係：對每個元件尋找面積最小的父群組
                        # 先依面積排序 (由大到小)
                        for g in groups:
                            g["area"] = g.get("width", 0) * g.get("height", 0)
                        groups_sorted = sorted(groups, key=lambda x: x["area"], reverse=True)
                        
                        # 將 group 當作節點一樣，找出它的 parent
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
                            
                        # 處理 nodes 的 parent
                        for node in nodes:
                            parent_id = "1"
                            rel_x, rel_y = node["x"], node["y"]
                            node["width"] = 80
                            node["height"] = 80
                            
                            # 找出能包住它的最小 group
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

                        # 生成 XML Cells (先畫 Groups)
                        for g in groups_sorted:
                            gid = g["id"]
                            gname = g.get("name", "")
                            gtype = g.get("type", "vpc")
                            style = styles.get(gtype, styles["vpc"])
                            w, h = g.get("width", 200), g.get("height", 200)
                            pid = g["parent_id"]
                            rx, ry = g["rel_x"], g["rel_y"]
                            
                            cells.append(f'<mxCell id="{gid}" value="{gname}" style="{style}" vertex="1" parent="{pid}"><mxGeometry x="{rx}" y="{ry}" width="{w}" height="{h}" as="geometry"/></mxCell>')
                        
                        # 生成 XML Cells (Nodes)
                        for idx, node in enumerate(nodes):
                            node_id = node.get("id", f"node_{idx}")
                            comp = node.get("name", "Unknown")
                            pid = node["parent_id"]
                            rx, ry = node["rel_x"], node["rel_y"]
                            
                            chunk = json.dumps({"type": "progress", "content": f"🔄 正在取得 {comp.upper()} 圖示 ({idx+1}/{len(nodes)})..."})
                            yield f"data: {chunk}\n\n"
                            
                            svg_content = await fetch_icon_from_n8n(comp)
                            b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
                            style = f"shape=image;image=data:image/svg+xml,{b64_svg};verticalLabelPosition=bottom;verticalAlign=top;align=center;"
                            cells.append(f'<mxCell id="{node_id}" value="{comp.upper()}" style="{style}" vertex="1" parent="{pid}"><mxGeometry x="{rx}" y="{ry}" width="80" height="80" as="geometry"/></mxCell>')
                            
                        # 生成 XML Cells (Edges - 採用直角連線)
                        for idx, edge in enumerate(edges):
                            src = edge.get("source")
                            tgt = edge.get("target")
                            if src and tgt:
                                edge_id = f"edge_{idx}"
                                edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
                                cells.append(f'<mxCell id="{edge_id}" edge="1" parent="1" source="{src}" target="{tgt}" style="{edge_style}"><mxGeometry relative="1" as="geometry"/></mxCell>')
                                
                        inner_xml = "".join(cells)
                        xml_data = f"""<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>{inner_xml}</root></mxGraphModel>"""
                        
                        chunk = json.dumps({"type": "xml", "content": xml_data})
                        yield f"data: {chunk}\n\n"
                        
                except Exception as e:
                    print(f"Failed to parse tool arguments or draw: {e}")
                    chunk = json.dumps({"type": "error", "content": "產圖發生錯誤"})
                    yield f"data: {chunk}\n\n"
                    
        except Exception as e:
            print(f"Stream error: {e}")
            chunk = json.dumps({"type": "error", "content": "發生未預期錯誤"})
            yield f"data: {chunk}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
