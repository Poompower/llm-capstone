# 🐟 แมวกินปลา AI (CatEatFish Thai Sea Fish Assistant)
### Capstone Project — Building LLM-Powered Applications (KMITL)
**Developer:** Pongsatorn Kitjetnee  
**Repository:** [https://github.com/Poompower/llm-capstone](https://github.com/Poompower/llm-capstone)  
**Live Deployed App:** [https://cateatfish-ai.onrender.com](https://cateatfish-ai.onrender.com)  
**Knowledge Domain:** [CAT EAT FISH (แมวกินปลา) — ประมงพื้นบ้านบ้านน้ำเค็ม จ.พังงา](https://cateatfish.co/sea/thai-fish)  
**Model & Infrastructure:** `gemma-4-E4B-it` via Course Proxy (`https://llm.nat-d.uk/v1`), FastAPI, SQLite3  

---

## 📖 Project Overview

**CatEatFish AI** is an end-to-end LLM-powered culinary guide and sustainable fishery assistant built for **CAT EAT FISH (แมวกินปลา)**, grounded in authentic Thai sea fish data from [cateatfish.co/sea/thai-fish](https://cateatfish.co/sea/thai-fish).

The system seamlessly combines **Hybrid Retrieval-Augmented Generation (RAG)** over 40+ Thai edible sea fish species with a **Guarded Text-to-SQL ReAct Agent** over a cold-chain seafood inventory and order database (`store.db`), powered by `gemma-4-E4B-it` via the course proxy (`from openai import OpenAI`).

---

## 🎯 Course Capability Families Demonstrated (6 of 6)

| Family | Implementation in CatEatFish AI | Key Files |
| :--- | :--- | :--- |
| **1. Structured Output & Validation** | Pydantic request/response schemas (`ChatRequest`, `ChatResponse`) and defensive JSON tool-argument parsing | `main.py`, `src/tools.py` |
| **2. Retrieval / RAG (Cite)** | 5 Markdown documents (15 chunks) covering 40+ Thai sea fish species from `cateatfish.co/sea/thai-fish`, indexed with **BM25 + Thai Subword/Semantic TF-IDF + Reciprocal Rank Fusion (RRF, $k=60$)** and inline `[file.md # Section]` citations | `src/rag.py`, `data/knowledge/*.md` |
| **3. Retrieval & System Evaluation** | **30-case benchmark** (`eval/benchmark_data.json`) comparing **Naive BM25 Baseline** vs. **Improved Hybrid RAG** (`Recall@1`, `Recall@3`, `Recall@5`, `MRR`) + **Guarded SQL Execution Accuracy** | `eval/evaluate.py`, `eval/benchmark_data.json`, `eval/eval_results.json` |
| **4. Agent Loop with Tools** | Multi-turn **ReAct tool-calling loop** (`max_steps=5`) with `search_knowledge_base`, `query_database`, and `get_order_status` + non-empty response guarantee | `src/agent.py`, `src/tools.py` |
| **5. Advanced Capability (Guarded Text-to-SQL)** | Live SQLite schema introspection (`sqlite_master`) + 5-layer security guard (`SELECT`/CTE-only, no stacked `;`, no comments, banned keywords, automatic `LIMIT 100`) as taught in **Lecture 11** | `src/database.py`, `seed_db.py` |
| **6. Served Interface** | FastAPI REST backend serving a responsive **Thai Retro Neubrutalism Web UI** with live tool-call traces, citation badges, and interactive evaluation dashboard | `main.py`, `static/index.html`, `static/style.css`, `static/app.js` |

---

## 📊 Quantitative Evaluation Summary (30 Benchmark Cases)

Run `python evaluate.py` to reproduce the full benchmark:

| Metric | Baseline (BM25 Only) | Improved (Hybrid RAG + RRF) | Relative Lift |
| :--- | :---: | :---: | :---: |
| **Recall@1 (Top-1 Accuracy)** | `80.00%` | **`90.00%`** | **`+12.5%` lift** |
| **Recall@3** | `100.00%` | **`100.00%`** | `100% Coverage` |
| **Recall@5** | `100.00%` | **`100.00%`** | `100% Coverage` |
| **MRR (Mean Reciprocal Rank)** | `0.8833` | **`0.9500`** | **`+7.5%` lift** |
| **Guarded SQL Execution Accuracy** | N/A | **`100.00%` (10/10)** | Zero security leaks |

---

## 🏗️ System Architecture

```
User Query
   │
   ▼
FastAPI Backend (main.py)  ── Pydantic Request Validation
   │
   ▼
ReAct Agent Loop (src/agent.py)  ── gemma-4-E4B-it (Proxy: https://llm.nat-d.uk/v1)
   │
   ├── [Chit-chat] ──────────────────────────► Direct Conversational Reply
   │
   ├── [Tool: search_knowledge_base] ────────► Hybrid RAG Engine (src/rag.py)
   │                                              ├─ Okapi BM25 (Lexical)
   │                                              ├─ Subword 3/4-grams & Synonyms
   │                                              └─ Reciprocal Rank Fusion (RRF)
   │                                              └─ Citations: [file.md # Section]
   │
   └── [Tool: query_database / get_order] ───► Guarded Text-to-SQL (src/database.py)
                                                  ├─ DDL from sqlite_master
                                                  ├─ 5-Layer Security Guard
                                                  └─ SQLite store.db Execution
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Configure `.env`
```bash
git clone https://github.com/Poompower/llm-capstone.git
cd llm-capstone
```
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_course_proxy_key_here
OPENAI_BASE_URL=https://llm.nat-d.uk/v1
```

### 2. Install Dependencies & Seed Database
```bash
pip install -r requirements.txt
python seed_db.py
```

### 3. Run Unit Tests & Evaluation Benchmark
```bash
python -m unittest discover tests
python evaluate.py
```

### 4. Start Web Application
```bash
uvicorn main:app --reload --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📄 Deliverables Summary
- **Q1 — GitHub Repository:** [https://github.com/Poompower/llm-capstone](https://github.com/Poompower/llm-capstone)
- **Q2 — Project Report (PDF):** `docs/PROJECT_REPORT.pdf` (Rendered from `docs/PROJECT_REPORT.md`)
- **Q3 — Live App & Demo Link:** [https://cateatfish-ai.onrender.com](https://cateatfish-ai.onrender.com) (Script: `docs/DEMO_SCRIPT.md`)
