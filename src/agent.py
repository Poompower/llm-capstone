import time
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from src.config import MODEL_NAME, get_openai_client_and_base
from src.tools import get_tool_definitions, dispatch_tool

SYSTEM_PROMPT = """คุณคือ "แมวกินปลา AI (CatEatFish Thai Sea Fish Assistant)" ผู้เชี่ยวชาญด้านปลาทะเลไทยที่กินได้ อาหารทะเลพื้นบ้านฝั่งอันดามัน และระบบจัดการร้านค้าของ CAT EAT FISH (อ้างอิงข้อมูลจาก https://cateatfish.co/sea/thai-fish)

คุณมีเครื่องมือ (Tools) 3 รายการในการค้นหาข้อมูลจริง:
1. `search_knowledge_base`: ใช้ค้นหาข้อมูลชนิดปลาทะเลไทย ฤดูกาลที่พบมาก ลักษณะเนื้อปลา เมนูที่เหมาะและไม่เหมาะ (เช่น ซาชิมิ, ฟิชแอนด์ชิป, ลวกจิ้ม, นึ่ง, แกงส้ม, ปลาสำหรับเด็กและผู้สูงอายุ) รวมถึงวิถีประมงพื้นบ้านบ้านน้ำเค็ม จ.พังงา การเก็บรักษา -20°C และสูตรอาหาร ต้องอ้างอิงแหล่งที่มาเสมอ เช่น [trevally_and_pompano.md # 1. ปลากะมงขาวปลากะมงหน้าดำ และปลากะมงพร้าว]
2. `query_database`: ใช้รันคำสั่ง SQL SELECT (แบบอ่านอย่างเดียว) บนฐานข้อมูลร้านแมวกินปลา เพื่อตรวจสอบราคา จำนวนสต็อกคงเหลือ รายการสั่งซื้อ ยอดขาย หรือการเคลมสินค้า
3. `get_order_status`: ใช้ค้นหาสถานะคำสั่งซื้อและเลขพัสดุรถห้องเย็นอย่างรวดเร็วด้วยรหัสออเดอร์ (เช่น ORD-1001)

แนวทางการตอบคำถาม:
- เมื่อผู้ใช้ถามเกี่ยวกับชนิดปลา ลักษณะเนื้อ ฤดูกาล เมนูแนะนำ หรือปลาชนิดใดไม่เหมาะทำเมนูใด ให้เรียกใช้ `search_knowledge_base` และอ้างอิงแท็กแหล่งที่มา `[ชื่อไฟล์.md # หัวข้อ]` ในคำตอบเสมอ:
  * เมนูฟิชแอนด์ชิป (Fish & Chips): แนะนำ **ปลากะมงพร้าว** (มีมันใต้ชั้นหนังที่เกล็ดบาง ฟูกรอบง่ายเมื่อทอด) หรือ **ปลาสากหางเหลือง (ปลาน้ำดอกไม้)**
  * เมนูซาชิมิ (ทานดิบ): แนะนำ **ปลากะมงกล้วย**, **ปลาแชกำ**, **ปลาอินทรีย์**, **ปลาแดงจ๋า (กะพงแดงหน้าตั้ง)**, **ปลาสละ/ปลาเสียด** หรือ **หอยโนราห์**
  * เมนูสำหรับเด็กและผู้สูงอายุ: แนะนำ **ปลาเหลืองญี่ปุ่น** (เนื้อนุ่มมาก ก้างน้อย เคี้ยวง่าย รสชาติไม่ซับซ้อน)
  * เมนูสายคลีน / โอเมก้า 3 สูง: แนะนำ **ปลาอังเกย** (โอเมก้า 3 สูง เนื้อขาวละเอียด ไม่กระด้าง เหมาะทำข้าวอบปลาสไตล์ญี่ปุ่น)
  * ปลาที่ไม่เหมาะกับเมนูทอด: **ปลาเก๋าดอกดำ**, **ปลาเก๋าเพลิง**, **ปลาเก๋าดอกแดง** (เพราะหนังเหนียวเกินไป) และ **ปลาจ้าวสมุทร** (เพราะไขมันสูงทำให้เนื้อไหม้ง่าย)
  * ราชาแห่งปลาเค็ม: **ปลากุเลา**
- เมื่อผู้ใช้ถามเกี่ยวกับราคา สต็อก จำนวนออเดอร์ หรือสถิติในร้าน ให้เรียกใช้ `query_database` ด้วยคำสั่ง SQL SELECT ที่ถูกต้องและตอบตามข้อมูลจริงในฐานข้อมูลเท่านั้น
- สำหรับคำถามผสมผสาน (เช่น ขอคำแนะนำปลาทำซาชิมิพร้อมเช็คราคาและสต็อกในร้าน หรือเช็คออเดอร์พร้อมวิธีทำอาหารของปลาในออเดอร์นั้น) ให้เรียกใช้ทั้ง `search_knowledge_base` และ `query_database` / `get_order_status` แล้วสรุปคำตอบให้ครบถ้วน
- สำหรับการทักทาย ขอบคุณ หรือบอกลาทั่วไป (เช่น "สวัสดีครับ", "ขอบคุณมากครับ") ให้ตอบกลับอย่างสุภาพโดยไม่ต้องเรียกใช้เครื่องมือ
- ตอบกลับเป็นภาษาไทยที่ชัดเจน สุภาพ และมีรายละเอียดครบถ้วน ห้ามส่งข้อความว่างเปล่าเด็ดขาด
"""

def run_agent_turn(
    user_message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    max_steps: int = 5,
    temperature: float = 0.0
) -> Dict[str, Any]:
    """
    Executes a complete ReAct agent turn using OpenAI native tool calling.
    Enforces loop termination (max_steps), guarantees non-empty responses,
    and captures execution traces.
    """
    start_time = time.time()
    api_key, base_url = get_openai_client_and_base()

    if not api_key:
        return {
            "reply": "ข้อผิดพลาด: ไม่พบ OPENAI_API_KEY ในตัวแปรสภาพแวดล้อม (Environment Variables)",
            "tools_called": [],
            "citations": [],
            "sql_queries": [],
            "steps": 0,
            "latency_ms": 0,
            "error": "Missing API Key"
        }

    client = OpenAI(api_key=api_key, base_url=base_url)
    tools = get_tool_definitions()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        for msg in conversation_history[-6:]:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg.get("content", "")})

    messages.append({"role": "user", "content": user_message})

    trace_tools_called = []
    collected_citations = []
    executed_sql = []
    step_count = 0

    while step_count < max_steps:
        step_count += 1
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature
            )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "reply": f"ข้อผิดพลาดจาก Upstream LLM: {str(e)}",
                "tools_called": trace_tools_called,
                "citations": list(set(collected_citations)),
                "sql_queries": executed_sql,
                "steps": step_count,
                "latency_ms": latency_ms,
                "error": str(e)
            }

        msg = response.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)

        # 1. Natural termination: model emits content with no tool calls
        if not tool_calls:
            reply_text = (msg.content or "").strip()

            # If the model finished tools but returned empty content, force prose summary with tool_choice="none"
            if not reply_text and trace_tools_called:
                try:
                    final_resp = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=messages,
                        tool_choice="none",
                        temperature=temperature
                    )
                    reply_text = (final_resp.choices[0].message.content or "").strip()
                except Exception:
                    pass

            # Safe backstop: ensure reply is never empty under any circumstance
            if not reply_text:
                if trace_tools_called:
                    reply_text = (
                        "จากการตรวจสอบข้อมูลปลาทะเลไทยและฐานข้อมูลร้านแมวกินปลา พบรายละเอียดตามที่ปรากฏในบันทึกเครื่องมือข้างต้น "
                        "หากคุณต้องการสอบถามเมนูปลา ฤดูกาล หรือตรวจสอบรายการสินค้าเพิ่มเติม แจ้งได้เลยครับ!"
                    )
                else:
                    reply_text = (
                        "สวัสดีครับ ยินดีต้อนรับสู่ แมวกินปลา AI (CatEatFish) "
                        "สอบถามข้อมูลปลาทะเลไทยที่กินได้ เมนูแนะนำ ฤดูกาล หรือเช็คสต็อกและสถานะคำสั่งซื้อได้เลยครับ!"
                    )

            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "reply": reply_text,
                "tools_called": trace_tools_called,
                "citations": list(set(collected_citations)),
                "sql_queries": executed_sql,
                "steps": step_count,
                "latency_ms": latency_ms
            }

        # 2. Model requested one or more tool calls: append assistant turn
        messages.append(msg)

        # 3. Execute all tool calls in this turn and feed results back as role: 'tool'
        for call in tool_calls:
            call_id = call.id
            tool_name = call.function.name
            tool_args_raw = call.function.arguments

            # Dispatch tool execution defensively
            res = dispatch_tool(tool_name, tool_args_raw)

            # Record citations & sql for trace
            if "citations" in res:
                collected_citations.extend(res["citations"])
            if "query" in res:
                executed_sql.append(res["query"])

            trace_tools_called.append({
                "step": step_count,
                "tool": tool_name,
                "args": tool_args_raw,
                "success": res.get("success", False),
                "summary": res.get("content", "")[:160] + "..." if len(res.get("content", "")) > 160 else res.get("content", "")
            })

            # Append tool message (Lecture 10 & 11)
            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": res.get("content", "")
            })

    # If max_steps is hit without natural stop, force a final summary answer with tool_choice="none"
    try:
        final_resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tool_choice="none",
            temperature=temperature
        )
        reply = (final_resp.choices[0].message.content or "").strip()
        if not reply:
            reply = "ระบบได้รวบรวมข้อมูลปลาทะเลไทยและรายการสินค้าตามที่ท่านสอบถามเรียบร้อยแล้ว หากต้องการข้อมูลใดเพิ่มเติมสามารถแจ้งได้เลยครับ!"
    except Exception:
        reply = "ระบบได้รวบรวมข้อมูลปลาทะเลไทยและรายการสินค้าตามที่ท่านสอบถามเรียบร้อยแล้ว หากต้องการข้อมูลใดเพิ่มเติมสามารถแจ้งได้เลยครับ!"

    latency_ms = int((time.time() - start_time) * 1000)
    return {
        "reply": reply,
        "tools_called": trace_tools_called,
        "citations": list(set(collected_citations)),
        "sql_queries": executed_sql,
        "steps": step_count,
        "latency_ms": latency_ms
    }
