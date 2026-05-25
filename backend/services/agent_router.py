from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@router.post("/generate")
def chat_and_generate(request: ChatRequest):
    messages = request.messages
    if not messages:
        raise HTTPException(status_code=400, detail="對話不可為空")
        
    last_user_msg = ""
    for msg in reversed(messages):
        if msg.role == "user":
            last_user_msg = msg.content.lower()
            break
            
    # 處理資源衝突檢測
    if "衝突" in last_user_msg or "conflict" in last_user_msg:
        raise HTTPException(status_code=400, detail="資源衝突：所選區域不支援該服務")
        
    # 分析歷史紀錄中的所有需求
    full_text = " ".join([m.content.lower() for m in messages if m.role == "user"])
    
    needs_db = "資料庫" in full_text or "aurora" in full_text or "db" in full_text
    needs_cache = "快取" in full_text or "redis" in full_text or "elasticache" in full_text
    needs_waf = "waf" in full_text or "防護" in full_text
    needs_ha = "ha" in full_text or "高可用" in full_text
    is_ecommerce = "電商" in full_text or "購物" in full_text
    
    response_msg = ""
    xml_data = ""
    
    # State Machine (Mock LLM Agent)
    if is_ecommerce and not needs_db and not needs_cache:
        response_msg = "好的！想建立一個電商網站。請問您的電商網站預計會有高流量嗎？是否需要資料庫（如 Aurora）與快取機制（如 Redis）來加速？"
    elif not needs_db and not needs_waf and not is_ecommerce:
        response_msg = "收到您的需求。為了確保架構完整，請問您需要加入資料庫或是特定的安全性防護（例如 WAF）嗎？"
    else:
        response_msg = "了解，根據您的需求，我已經為您規劃了合適的雲端架構圖。您可以在右側檢視，如果需要調整（例如加入 WAF 或 Redis），請直接告訴我！"
        
        # 產生複雜架構圖 XML (基於需求)
        cells = []
        y_pos = 120
        
        # VPC / AZ Box
        cells.append('<mxCell id="vpc" value="VPC (10.0.0.0/16)" style="rounded=1;whiteSpace=wrap;html=1;dashed=1;align=left;verticalAlign=top;fillColor=none;strokeColor=#b85450;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="720" height="500" as="geometry"/></mxCell>')
        
        if needs_ha:
             cells.append('<mxCell id="az1" value="Availability Zone A" style="rounded=0;whiteSpace=wrap;html=1;dashed=1;align=left;verticalAlign=top;fillColor=none;strokeColor=#d79b00;" vertex="1" parent="vpc"><mxGeometry x="20" y="40" width="320" height="440" as="geometry"/></mxCell>')
             cells.append('<mxCell id="az2" value="Availability Zone B" style="rounded=0;whiteSpace=wrap;html=1;dashed=1;align=left;verticalAlign=top;fillColor=none;strokeColor=#d79b00;" vertex="1" parent="vpc"><mxGeometry x="360" y="40" width="320" height="440" as="geometry"/></mxCell>')
        else:
             cells.append('<mxCell id="az1" value="Availability Zone A" style="rounded=0;whiteSpace=wrap;html=1;dashed=1;align=left;verticalAlign=top;fillColor=none;strokeColor=#d79b00;" vertex="1" parent="vpc"><mxGeometry x="20" y="40" width="660" height="440" as="geometry"/></mxCell>')
             
        # WAF
        if needs_waf:
            cells.append('<mxCell id="waf" value="AWS WAF" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1"><mxGeometry x="340" y="100" width="120" height="60" as="geometry"/></mxCell>')
            
        # ALB
        cells.append('<mxCell id="alb" value="Application Load Balancer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1"><mxGeometry x="320" y="200" width="160" height="60" as="geometry"/></mxCell>')
        
        # EC2
        cells.append('<mxCell id="ec2_1" value="EC2 Instance (Web)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1"><mxGeometry x="120" y="300" width="120" height="60" as="geometry"/></mxCell>')
        if needs_ha:
            cells.append('<mxCell id="ec2_2" value="EC2 Instance (Web)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1"><mxGeometry x="500" y="300" width="120" height="60" as="geometry"/></mxCell>')
            
        # DB
        if needs_db:
            cells.append('<mxCell id="db" value="Amazon Aurora" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1"><mxGeometry x="140" y="420" width="80" height="80" as="geometry"/></mxCell>')
        
        # Redis
        if needs_cache:
            cells.append('<mxCell id="redis" value="ElastiCache (Redis)" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1"><mxGeometry x="520" y="420" width="80" height="80" as="geometry"/></mxCell>')
            
        # Connections
        if needs_waf:
            cells.append('<mxCell id="edge1" edge="1" parent="1" source="waf" target="alb"><mxGeometry relative="1" as="geometry"/></mxCell>')
        
        cells.append('<mxCell id="edge2" edge="1" parent="1" source="alb" target="ec2_1"><mxGeometry relative="1" as="geometry"/></mxCell>')
        if needs_ha:
            cells.append('<mxCell id="edge3" edge="1" parent="1" source="alb" target="ec2_2"><mxGeometry relative="1" as="geometry"/></mxCell>')
            
        if needs_db:
            cells.append('<mxCell id="edge4" edge="1" parent="1" source="ec2_1" target="db"><mxGeometry relative="1" as="geometry"/></mxCell>')
            if needs_ha:
                cells.append('<mxCell id="edge5" edge="1" parent="1" source="ec2_2" target="db"><mxGeometry relative="1" as="geometry"/></mxCell>')
                
        if needs_cache:
            cells.append('<mxCell id="edge6" edge="1" parent="1" source="ec2_1" target="redis"><mxGeometry relative="1" as="geometry"/></mxCell>')
            if needs_ha:
                cells.append('<mxCell id="edge7" edge="1" parent="1" source="ec2_2" target="redis"><mxGeometry relative="1" as="geometry"/></mxCell>')

        inner_xml = "".join(cells)
        xml_data = f"""<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>{inner_xml}</root></mxGraphModel>"""
    
    return {
        "status": "success", 
        "message": response_msg,
        "xml": xml_data if xml_data else None
    }
