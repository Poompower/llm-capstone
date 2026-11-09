import json
from typing import Dict, Any, List
from src.database import get_schema_prompt, execute_guarded_sql, get_order_by_id
from src.rag import get_rag_system

def get_tool_definitions() -> List[Dict[str, Any]]:
    schema_ddl = get_schema_prompt()
    return [
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": (
                    "ค้นหาคลังความรู้เกี่ยวกับปลาทะเลไทยที่กินได้ อาหารทะเลพื้นบ้าน ฤดูกาลที่พบ ลักษณะเนื้อปลา "
                    "เมนูที่เหมาะและไม่เหมาะ (เช่น ซาชิมิ, ฟิชแอนด์ชิป, ลวกจิ้ม, นึ่ง, แกงส้ม, ปลาสำหรับเด็กและผู้สูงอายุ) "
                    "รวมถึงข้อมูลประมงพื้นบ้านบ้านน้ำเค็ม จ.พังงา มาตรฐานแช่เยือกแข็ง -20°C และสูตรอาหารจาก cateatfish.co/sea/thai-fish "
                    "ควรใช้คำค้นหาภาษาไทยหรือชื่อปลาที่ตรงประเด็น เช่น 'ปลากะมงพร้าว ฟิชแอนด์ชิป', 'ปลาเก๋าดอกดำ หนังเหนียว ไม่เหมาะทอด', "
                    "'ปลาเหลืองญี่ปุ่น เด็ก ผู้สูงอายุ', 'ประมงพื้นบ้าน บ้านน้ำเค็ม มอแกลน'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "คำค้นหาเกี่ยวกับชนิดปลาทะเลไทย ลักษณะเนื้อ เมนูอาหาร ฤดูกาล หรือการประมงพื้นบ้าน"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_database",
                "description": (
                    "รันคำสั่ง SQL SELECT (แบบอ่านอย่างเดียว) บนฐานข้อมูลร้านแมวกินปลา (SQLite store.db) "
                    f"โครงสร้างตารางฐานข้อมูล (Schema):\n{schema_ddl}\n"
                    "ใช้สำหรับตรวจสอบราคาปลาแต่ละชนิด จำนวนสต็อกคงเหลือ ยอดสั่งซื้อของลูกค้า สถานะจัดส่งห้องเย็น หรือรายการเคลมสินค้า"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "คำสั่ง SQL SELECT แบบอ่านอย่างเดียว ห้ามใช้คำสั่งแก้ไขฐานข้อมูล เช่น DROP/INSERT/UPDATE"
                        }
                    },
                    "required": ["sql_query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_order_status",
                "description": (
                    "ค้นหาข้อมูลคำสั่งซื้ออย่างรวดเร็วด้วยรหัสคำสั่งซื้อ (เช่น 'ORD-1001') "
                    "คืนค่าสถานะจัดส่ง ชื่อลูกค้า รหัสพัสดุรถควบคุมอุณหภูมิ (COOL-...) และรายการปลาที่สั่งซื้อ"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "รหัสคำสั่งซื้อ เช่น ORD-1001"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        }
    ]

def dispatch_tool(name: str, raw_args: Any) -> Dict[str, Any]:
    """
    Defensively executes a requested tool (Lecture 10 & 13):
      - Handles arguments as string or dict
      - Catches errors and returns an error dict/string instead of crashing
      - Returns structured result and citation/metadata
    """
    # 1. Parse arguments defensively
    if isinstance(raw_args, str):
        try:
            args = json.loads(raw_args) if raw_args.strip() else {}
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid JSON arguments: {str(e)}",
                "content": f"Error: Could not parse arguments as JSON: {raw_args}"
            }
    elif isinstance(raw_args, dict):
        args = raw_args
    else:
        args = {}

    # 2. Dispatch
    if name == "search_knowledge_base":
        query = args.get("query", "").strip()
        if not query:
            return {"success": False, "error": "Argument 'query' is required", "content": "Error: query cannot be empty"}
        rag = get_rag_system()
        hits = rag.search_hybrid(query, top_k=3)
        if not hits:
            return {
                "success": True,
                "citations": [],
                "content": "No relevant documents found matching query.",
                "data": []
            }
        
        passages = []
        citations = []
        for h in hits:
            citations.append(h["citation"])
            passages.append(f"Source {h['citation']}:\n{h['text']}")
        
        return {
            "success": True,
            "citations": citations,
            "content": "\n\n---\n\n".join(passages),
            "data": hits
        }

    elif name == "query_database":
        sql = args.get("sql_query", "").strip()
        if not sql:
            return {"success": False, "error": "Argument 'sql_query' is required", "content": "Error: sql_query cannot be empty"}
        res = execute_guarded_sql(sql)
        if not res.get("success", False):
            return {
                "success": False,
                "error": res.get("error"),
                "content": f"Database Error: {res.get('error')}"
            }
        
        rows = res.get("rows", [])
        if not rows:
            return {
                "success": True,
                "content": f"Query returned 0 rows. (SQL: {res.get('query')})",
                "data": [],
                "query": res.get("query")
            }
        
        return {
            "success": True,
            "content": json.dumps(rows, indent=2, ensure_ascii=False),
            "data": rows,
            "query": res.get("query")
        }

    elif name == "get_order_status":
        order_id = args.get("order_id", "").strip()
        if not order_id:
            return {"success": False, "error": "Argument 'order_id' is required", "content": "Error: order_id cannot be empty"}
        res = get_order_by_id(order_id)
        return {
            "success": True,
            "content": json.dumps(res, indent=2, ensure_ascii=False),
            "data": res
        }

    else:
        return {
            "success": False,
            "error": f"Unknown tool: '{name}'",
            "content": f"Error: Tool '{name}' is not recognized."
        }
