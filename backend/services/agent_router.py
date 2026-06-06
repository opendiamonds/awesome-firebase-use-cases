import os
import json
import base64
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

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
                        item = data[0]
                        if "svg_content" in item:
                            return item["svg_content"]
                        if "svg" in item:
                            return item["svg"]
                            
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
async def chat_and_generate(request: ChatRequest):
    messages = request.messages
    if not messages:
        raise HTTPException(status_code=400, detail="對話不可為空")
        
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not openrouter_key and not anthropic_key:
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
            raise HTTPException(status_code=500, detail="未提供 OPENROUTER_API_KEY")
            
        model_name = os.environ.get("LLM_MODEL", "anthropic/claude-sonnet-4.6")
        
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
            
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
            if resp.status_code != 200:
                print(f"OpenRouter Error: {resp.text}")
                raise HTTPException(status_code=500, detail="OpenRouter API 呼叫失敗")
                
            try:
                resp_json = resp.json()
                response_text = resp_json["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"OpenRouter Raw Response (Failed to parse JSON): {resp.text}")
                response_text = ""
            
        # Try parsing JSON
        try:
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if Claude returns markdown wrapped json
            try:
                cleaned = response_text.replace("```json", "").replace("```", "").strip()
                parsed_data = json.loads(cleaned)
            except Exception:
                # 處理 LLM 完全沒有輸出 JSON，只給純文字回覆的狀況
                parsed_data = {
                    "reply_message": response_text.strip(),
                    "generate_ready": False,
                    "components": []
                }
            
        reply_message = parsed_data.get("reply_message", "好的，我了解了。")
        generate_ready = parsed_data.get("generate_ready", False)
        components = parsed_data.get("components", [])
        
    except Exception as e:
        print(f"Claude API Error: {e}")
        raise HTTPException(status_code=500, detail=f"呼叫 Claude API 發生錯誤: {str(e)}")
        
    xml_data = ""
    
    if generate_ready and components:
        cells = []
        # Background VPC
        cells.append('<mxCell id="vpc" value="AWS Cloud / VPC" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;align=left;verticalAlign=top;fillColor=none;strokeColor=#b85450;fontSize=18;fontStyle=1" vertex="1" parent="1"><mxGeometry x="40" y="40" width="800" height="600" as="geometry"/></mxCell>')
        
        x, y = 100, 100
        prev_comp = None
        
        for idx, comp in enumerate(components):
            svg_content = await fetch_icon_from_n8n(comp)
            b64_svg = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
            
            # draw.io image style with embedded SVG
            style = f"shape=image;image=data:image/svg+xml;base64,{b64_svg};verticalLabelPosition=bottom;verticalAlign=top;align=center;"
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
        xml_data = f"""<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>{inner_xml}</root></mxGraphModel>"""
    
    return {
        "status": "success", 
        "message": reply_message,
        "xml": xml_data if xml_data else None
    }
