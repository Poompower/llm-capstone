# 🐟 แมวกินปลา AI (CatEatFish Thai Sea Fish Assistant) — LLM Capstone Project

An end-to-end LLM-powered culinary & sustainable fishery assistant built for **CAT EAT FISH (แมวกินปลา)**, grounded in authentic Thai edible sea fish data from [https://cateatfish.co/sea/thai-fish](https://cateatfish.co/sea/thai-fish).

The system combines **Hybrid Retrieval-Augmented Generation (RAG)** over 40+ Thai sea fish species with a **Guarded Text-to-SQL ReAct Agent** over a cold-chain seafood inventory & order database (`store.db`), powered by the course proxy (`model="gemma-4-E4B-it"` via `from openai import OpenAI`).

---

## 🎯 Course Capability Families Demonstrated (6 of 6)

| Family | Implementation in CatEatFish AI | Key Files |
| :--- | :--- | :--- |
| **1. Structured Output & Validation** | Pydantic request/response schemas (`ChatRequest`, `ChatResponse`) and defensive JSON tool-argument parsing | `main.py`, `src/tools.py` |
| **2. Retrieval / RAG (Cite)** | 5 Markdown documents (15 chunks) covering 40+ Thai sea fish species from `cateatfish.co/sea/thai-fish`, indexed with **BM25 + Thai Subword/Semantic TF-IDF + Reciprocal Rank Fusion (RRF)** and inline `[file.md # Section]` citations | `src/rag.py`, `data/knowledge/*.md` |
| **3. Retrieval & System Evaluation** | **30-case benchmark** (`eval/benchmark_data.json`) comparing **Naive BM25 Baseline** vs. **Improved Hybrid RAG** (`Recall@1`, `Recall@3`, `Recall@5`, `MRR`) + **Guarded SQL Execution Accuracy** | `eval/evaluate.py`, `eval/benchmark_data.json`, `eval/eval_results.json` |
| **4. Agent Loop with Tools** | Multi-turn **ReAct tool-calling loop** (`max_steps=5`) with `search_knowledge_base`, `query_database`, and `get_order_status` + non-empty response guarantee | `src/agent.py`, `src/tools.py` |
| **5. Advanced Capability (Guarded Text-to-SQL)** | Live SQLite schema introspection (`sqlite_master`) + 5-layer security guard (`SELECT`-only, no stacked `;`, no comments, banned write keywords, automatic `LIMIT 100`) | `src/database.py`, `seed_db.py` |
| **6. Served Interface** | FastAPI REST backend serving a responsive **Thai Retro Neubrutalism Web UI** with live tool-call traces, citation badges, and interactive evaluation dashboard | `main.py`, `static/index.html`, `static/style.css`, `static/app.js` |

---

## 📊 Quantitative Evaluation Summary (30 Test Cases)

Run `python evaluate.py` to reproduce the full benchmark:

| Metric | Baseline (BM25 Only) | Improved (Hybrid RAG + RRF) | Relative Lift |
| :--- | :---: | :---: | :---: |
| **Recall@1 (Top-1 Accuracy)** | `80.00%` | **`90.00%`** | **`+12.5%`** |
| **Recall@3** | `100.00%` | **`100.00%`** | `100% Coverage` |
| **Recall@5** | `100.00%` | **`100.00%`** | `100% Coverage` |
| **MRR (Mean Reciprocal Rank)** | `0.8833` | **`0.9500`** | **`+7.5%`** |
| **Guarded SQL Execution Accuracy** | N/A | **`100.00%` (10/10)** | Verified against `store.db` |

---

## 🚀 Quickstart & Local Setup

### 1. Configure `.env`
Create a `.env` file in the project root (`d:\Desktop\llm-capstone\.env`):
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

### 4. Start the Web Server
```bash
uvicorn main:app --reload --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.
