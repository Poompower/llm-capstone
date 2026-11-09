import os
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import MODEL_NAME, get_openai_client_and_base
from src.agent import run_agent_turn
from src.rag import get_rag_system
from src.database import get_db_connection
from eval.evaluate import run_evaluation

app = FastAPI(
    title="CatEatFish AI — ปลาทะเลไทยที่กินได้",
    description="End-to-end Capstone LLM application for Thai Edible Sea Fish (cateatfish.co/sea/thai-fish) with Agentic Hybrid RAG, Guarded Text-to-SQL, and Quantitative Evaluation",
    version="1.0.0"
)

# Enable CORS for local testing / production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User question or query")
    temperature: float = Field(0.0, ge=0.0, le=2.0, description="Temperature (0.0 for deterministic tool execution)")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Recent conversation turns")

class ChatResponse(BaseModel):
    reply: str
    tools_called: List[Dict[str, Any]]
    citations: List[str]
    sql_queries: List[str]
    steps: int
    latency_ms: int
    model: str

@app.get("/api/health")
def health():
    rag = get_rag_system()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM products;")
    product_count = cur.fetchone()[0]
    conn.close()
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "knowledge_chunks_loaded": len(rag.chunks),
        "products_in_db": product_count
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    history_dicts = [{"role": m.role, "content": m.content} for m in req.history] if req.history else []
    result = run_agent_turn(
        user_message=req.message,
        conversation_history=history_dicts,
        temperature=req.temperature
    )

    if result.get("error"):
        # If upstream authentication/network error occurs
        if "API Key" in result["error"]:
            raise HTTPException(status_code=500, detail=result["reply"])
        raise HTTPException(status_code=502, detail=result["reply"])

    return ChatResponse(
        reply=result["reply"],
        tools_called=result.get("tools_called", []),
        citations=result.get("citations", []),
        sql_queries=result.get("sql_queries", []),
        steps=result.get("steps", 1),
        latency_ms=result.get("latency_ms", 0),
        model=MODEL_NAME
    )

@app.get("/api/evaluation")
def get_evaluation_results():
    results = run_evaluation()
    return results

@app.post("/api/evaluate")
def trigger_evaluation():
    results = run_evaluation()
    return results

@app.get("/api/sample-queries")
def get_sample_queries():
    return [
        {
            "category": "RAG (แนะนำปลาทำอาหาร)",
            "query": "ปลาทะเลไทยชนิดไหนเหมาะนำมาทำเมนูฟิชแอนด์ชิป (Fish & Chips) และเพราะอะไร?",
            "desc": "ทดสอบการค้นหาคลังความรู้ปลาทะเลไทยและแสดง Citation อ้างอิง"
        },
        {
            "category": "RAG (ข้อควรระวังในการปรุง)",
            "query": "ทำไมปลาเก๋าดอกดำและปลาเก๋าเพลิงถึงไม่เหมาะกับเมนูทอด และควรทำเมนูอะไรแทน?",
            "desc": "ทดสอบการดึงข้อมูลลักษณะเนื้อปลาและหนังปลาจากคู่มือปลาเก๋า"
        },
        {
            "category": "RAG (ปลาสำหรับเด็ก/ผู้สูงอายุ)",
            "query": "อยากหาปลาทะเลเนื้อนิ่ม ก้างน้อย เคี้ยวง่าย สำหรับเด็กและผู้สูงอายุ ควรเลือกปลาอะไร?",
            "desc": "ทดสอบ Semantic Search จับคู่คำถามกับปลาเหลืองญี่ปุ่นและปลาอังเกย"
        },
        {
            "category": "SQL (เช็คสต็อกและราคาปลา)",
            "query": "มีออเดอร์ที่กำลัง processing กี่รายการ และปลาชนิดใดบ้างที่สต็อกเหลือน้อยกว่า 15 แพค?",
            "desc": "ทดสอบ Guarded Text-to-SQL คำนวณจำนวนออเดอร์และสต็อกปลา"
        },
        {
            "category": "ผสมผสาน (RAG + SQL)",
            "query": "ปลาแชกำเกรดซาชิมิราคาแพคละกี่บาท มีสต็อกเท่าไหร่ และเนื้อปลาตอนกินดิบเป็นอย่างไร?",
            "desc": "Multi-hop: ค้นหาราคา/สต็อกจาก SQLite ผสานกับข้อมูลเนื้อปลาจาก RAG"
        },
        {
            "category": "ประมงพื้นบ้านพังงา",
            "query": "ชาวประมงพื้นบ้านและชาวมอแกลนที่บ้านน้ำเค็ม จ.พังงา ใช้เครื่องมืออะไรจับปลาอย่างยั่งยืน?",
            "desc": "ทดสอบการค้นหาที่มาของวัตถุดิบและวิถีประมงพื้นบ้านจาก cateatfish.co"
        }
    ]

# Serve frontend from ./static
app.mount("/", StaticFiles(directory="static", html=True), name="static")
