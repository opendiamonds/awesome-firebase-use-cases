import os
import json
import base64
import urllib.parse
import httpx
import logging
import asyncio
from fastapi import APIRouter, HTTPException, Depends
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
                # If n8n returns raw SVG
                content = response.text.strip()
                if content.startswith("<svg"):
                    return content
                # If n8n returns JSON
                try:
                    data = response.json()
                    
                    # 處理 n8n 直出資料庫陣列的狀況
                    if isinstance(data, list) and len(data) > 0:
                        matched_item = None
                        service_name_lower = service_name.lower()
                        
                        # 1. 精確子字串匹配
                        for item in data:
                            name = item.get("icon_name", "").lower()
                            if service_name_lower in name:
                                matched_item = item
                                break
                        
                        # 2. 如果沒匹配到，且 service_name 含有底線，拿各個單字去比對
                        if not matched_item and "_" in service_name_lower:
                            parts = [p for p in service_name_lower.split("_") if p not in ["web", "group", "service"]]
                            for part in parts:
                                if len(part) > 1:
                                    for item in data:
                                        name = item.get("icon_name", "").lower()
                                        if part in name:
                                            matched_item = item
                                            break
                                    if matched_item:
                                        break
                                        
                        # 3. 專屬 Alias 映射比對
                        if not matched_item:
                            aliases = {
                                "alb": ["elastic load balancing", "load balancing", "load-balancer", "loadbalancer", "elb"],
                                "redis": ["elasticache", "cache"],
                                "ec2_web": ["ec2", "virtual-server"]
                            }
                            if service_name_lower in aliases:
                                for alias in aliases[service_name_lower]:
                                    for item in data:
                                        name = item.get("icon_name", "").lower()
                                        if alias in name:
                                            matched_item = item
                                            break
                                    if matched_item:
                                        break

                        # 4. 如果最終都沒匹配到，就 fallback 拿第一個項目
                        if not matched_item:
                            matched_item = data[0]

                        if "svg_content" in matched_item:
                            return matched_item["svg_content"]
                        if "svg" in matched_item:
                            return matched_item["svg"]
                            
                    # 處理包在物件內的狀況
                    elif isinstance(data, dict):
                        if "svg_content" in data:
                            return data["svg_content"]
                        if "svg" in data:
                            return data["svg"]
                        if "data" in data and "svg" in data["data"]:
                            return data["data"]["svg"]
                            
                    print(f"Warning: Unexpected JSON format from n8n: {str(data)[:100]}")
                except Exception as e:
                    print(f"Error parsing n8n response: {str(e)}")
    except Exception as e:
        print(f"Failed to fetch icon for {service_name} from n8n: {e}")
        
    return fallback_svg

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
    請仔細閱讀對話歷史，判斷需求是否足夠明確（例如：是否知道需要哪些運算資源、資料庫、快取、資安防護等）。
    
    如果你需要更多資訊，請溫和地反問使用者。
    如果需求已經足夠明確，你可以決定產出架構圖。
    
    你必須且只能回傳 JSON 格式字串，格式如下：
    {
      "reply_message": "給使用者的文字回覆",
      "generate_ready": true 或 false (代表是否要開始畫圖),
      "components": ["waf", "alb", "ec2_web", "aurora", "redis"] (若 generate_ready 為 false，則可為空陣列)
    }
    
    請不要輸出 JSON 以外的任何文字。
    """
    
    response_text = ""
    
    try:
        if not openrouter_key:
            logger.error("錯誤: OPENROUTER_API_KEY 遺失")
            raise HTTPException(status_code=500, detail="未提供 OPENROUTER_API_KEY")
            
        model_name = os.environ.get("LLM_MODEL", "anthropic/claude-sonnet-4.6")
        logger.info(f"準備呼叫 OpenRouter API. 模型: {model_name}")
        
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
            
        logger.info("傳送給 OpenRouter 的對話長度為 %d 筆", len(formatted_messages))
        
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": formatted_messages,
                    "temperature": 0.3
                },
                timeout=30.0
            )
            
            logger.info(f"OpenRouter API 回應狀態碼: {resp.status_code}")
            
            if resp.status_code != 200:
                logger.error(f"OpenRouter Error Detail: {resp.text}")
                raise HTTPException(status_code=500, detail="OpenRouter API 呼叫失敗")
                
            try:
                resp_json = resp.json()
                response_text = resp_json["choices"][0]["message"]["content"]
                logger.info("OpenRouter 回應內容獲取成功")
            except Exception as e:
                logger.error(f"解析 OpenRouter JSON 失敗. 回應內容: {resp.text}")
                response_text = ""
            
        # Try parsing JSON
        logger.info(f"開始解析 LLM 傳回之 JSON. 原始字串: {response_text}")
        try:
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if Claude returns markdown wrapped json
            try:
                cleaned = response_text.replace("```json", "").replace("```", "").strip()
                parsed_data = json.loads(cleaned)
            except Exception as e:
                logger.warning(f"JSON 結構解析失敗，Fallback 為純文字處置: {str(e)}")
                # 處理 LLM 完全沒有輸出 JSON，只給純文字回覆的狀況
                parsed_data = {
                    "reply_message": response_text.strip(),
                    "generate_ready": False,
                    "components": []
                }
            
        reply_message = parsed_data.get("reply_message", "好的，我了解了。")
        generate_ready = parsed_data.get("generate_ready", False)
        components = parsed_data.get("components", [])
        
        logger.info(f"解析後狀態: generate_ready={generate_ready}, components={components}")
        
    except Exception as e:
        logger.error(f"Claude/OpenRouter API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"呼叫 Claude API 發生錯誤: {str(e)}")
        
    xml_data = ""
    
    if generate_ready and components:
        cells = []
        
        # 併行（Parallel）向 n8n Webhook 抓取所有元件 of SVG 圖示，縮短 sequential 請求所產生的 loading 時間
        webhook_url = os.environ.get("N8N_WEBHOOK_URL")
        logger.info(f"開始抓取元件圖示. N8N Webhook URL: {'設定已啟用' if webhook_url else '未設定，將使用內建 Fallback SVG'}")
        
        # 使用 asyncio.gather 來加速抓取
        svg_contents = await asyncio.gather(*(fetch_icon_from_n8n(comp) for comp in components))
        logger.info("元件圖示抓取程序已完成。")
        
        # Background VPC
        cells.append('<mxCell id="vpc" value="AWS Cloud / VPC" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;align=left;verticalAlign=top;fillColor=none;strokeColor=#b85450;fontSize=18;fontStyle=1" vertex="1" parent="1"><mxGeometry x="40" y="40" width="800" height="600" as="geometry"/></mxCell>')
        
        x, y = 100, 100
        prev_comp = None
        
        for idx, (comp, svg_content) in enumerate(zip(components, svg_contents)):
            # 1. 將 SVG 以 Base64 編碼
            b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
            # 2. 不要在頭部使用分號，使用逗號分隔，讓 draw.io 在內部自動補上 ";base64"
            # 這樣既可避免分號被 style 解析器截斷，又能讓 draw.io 自動還原出正確的 base64 格式
            image_src = f"data:image/svg+xml,{b64_svg}"
            
            # 在樣式中直接嵌入沒有分號的 Data URI
            style = f"shape=image;image={image_src};verticalLabelPosition=bottom;verticalAlign=top;align=center;"
            comp_id = f"comp_{idx}"
            
            cells.append(f'<mxCell id="{comp_id}" value="{comp.upper()}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="80" height="80" as="geometry"/></mxCell>')
            
            if prev_comp:
                # Add connection
                cells.append(f'<mxCell id="edge_{idx}" edge="1" parent="1" source="{prev_comp}" target="{comp_id}"><mxGeometry relative="1" as="geometry"/></mxCell>')
            
            prev_comp = comp_id
            
            x += 150
            if x > 600:
                x = 100
                y += 150
                
        inner_xml = "".join(cells)
        # 返回最標準且相容的 mxGraphModel 結構
        xml_data = f"""<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>{inner_xml}</root></mxGraphModel>"""
        logger.info("架構圖 XML 組裝完成")
    
    logger.info("API 處理完畢，準備返回結果")
    logger.info("========================================")
    
    return {
        "status": "success", 
        "message": reply_message,
        "xml": xml_data if xml_data else None
    }
