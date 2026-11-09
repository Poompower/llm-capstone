# CatEatFish AI (แมวกินปลา AI) — Capstone Project Report
**Course:** Building LLM-Powered Applications (KMITL)  
**Student Name:** Pongsatorn Kitjetnee  
**Project Title:** CatEatFish AI — Intelligent Thai Sea Fish Culinary Guide & Cold-Chain Fishery Assistant  
**Data Domain:** [CAT EAT FISH (แมวกินปลา) — ประมงพื้นบ้านบ้านน้ำเค็ม จ.พังงา](https://cateatfish.co/sea/thai-fish)  
**Repository:** [https://github.com/Poompower/llm-capstone](https://github.com/Poompower/llm-capstone)  
**Model & Infrastructure:** `gemma-4-E4B-it` via Course Proxy (`https://llm.nat-d.uk/v1`), FastAPI, SQLite3  

---

## 1. Problem Statement, Target Audience & Real-World Domain

### 1.1 The Domain & Problem
Thailand's Andaman Sea and Gulf of Thailand boast extraordinary biodiversity, with over 40 species of edible local sea fish harvested sustainably by artisanal small-scale fishers—such as the Baan Nam Khem community and Moken sea nomads in Phang Nga province. Despite this rich heritage, urban consumers, home cooks, and modern culinary businesses face critical knowledge and operational barriers:
1. **Culinary Ignorance & Mispreparation:** Most Thai consumers only recognize commercial caged fish (e.g., seabass or salmon). Local species such as **ปลากะมงพร้าว (Giant Trevally)**, **ปลาแชกำ (Yellowspotted Trevally)**, **ปลาเหลืองญี่ปุ่น**, **ปลาอังเกย (Golden Snapper)**, or **ปลาจ้าวสมุทร** have vastly different meat textures, fat ratios, and skin thickness. Cooking them improperly—such as deep-frying thick-skinned groupers (`ปลาเก๋าดอกดำ`, `ปลาเก๋าเพลิง`) or high-fat belly fish (`ปลาจ้าวสมุทร`)—ruins the dish completely.
2. **Disconnected Inventory & Logistics:** Sustainable seafood enterprises like CAT EAT FISH flash-freeze catches at `-20°C` and ship them via cold-chain courier boxes (`COOL-...`). Customers constantly inquire about species characteristics in tandem with live commercial questions: *"Is Yellowspotted Trevally suitable for raw sashimi, how much does it cost per pack, and is it currently in stock?"*

### 1.2 Target Audience
- **Home Cooks & Seafood Enthusiasts:** Seeking trustworthy culinary advice on meat texture, cooking methods (Sashimi, Fish & Chips, steaming, curries), and kid/elderly-friendly fish selections.
- **Chefs & Restaurants:** Exploring sustainable, wild-caught Andaman fish alternatives to expensive imported fish.
- **Seafood Retail Customers:** Checking real-time cold-chain delivery status, prices, stock quantities, and freshness guarantee claims.

---

## 2. System Architecture & Course Techniques

CatEatFish AI implements an end-to-end multi-agent system combining **6 course capability families** (exceeding the course minimum of 3):

```
+-----------------------------------------------------------------------------------+
|                        Client Layer (Retro Neubrutalism UI)                       |
|   - Interactive Chat with Citation Badges   - Dynamic Tool-Call Traces Drawer     |
|   - Real-time 30-case Evaluation Visualizer - Store Database & Inventory Viewer   |
+-----------------------------------------------------------------------------------+
                                          |
                              (HTTP POST /api/chat)
                                          v
+-----------------------------------------------------------------------------------+
|                           FastAPI Backend (main.py)                               |
|   - Pydantic Schemas: ChatRequest, ChatResponse, ChatMessage (Family 1)           |
|   - CORS Middleware, Health Probes (/api/health), Static File Delivery (Family 6) |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               ReAct Agent Loop (src/agent.py - Families 4 & 5)                   |
|   - Model: gemma-4-E4B-it via Course OpenAI Proxy (temperature=0.0)              |
|   - Native OpenAI Tool Calling (tools=...) with Bounded Loop (max_steps=5)        |
|   - Empty-Response Fallback: forced synthesis via tool_choice="none"              |
+-----------------------------------------------------------------------------------+
         |                                                 |
         | (Tool Call: search_knowledge_base)              | (Tool Call: query_database /
         v                                                 |  get_order_status)
+---------------------------------------+                  v
|       Hybrid RAG Engine (Family 2)    |    +--------------------------------------+
| - Corpus: 5 Markdown Guides (15 Chks) |    |  Guarded Text-to-SQL (Lecture 11)    |
| - Lexical: Okapi BM25                 |    | - DDL Introspection: sqlite_master   |
| - Semantic: Subword N-grams + Synonyms|    | - 5-Layer Security Guard (guard_sql) |
| - Fusion: Reciprocal Rank Fusion (RRF)|    | - Read-Only: SELECT / CTEs only      |
| - Citation Injection: [file # section]|    | - Auto LIMIT 100 & Comment Rejection |
+---------------------------------------+    +--------------------------------------+
         |                                                 |
         +------------------------+------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------------------+
|                 Grounded Thai Synthesis with Attribution & Citations              |
+-----------------------------------------------------------------------------------+
```

### Detailed Course Techniques Coverage:
- **Family 1 — Structured Output & Schema Validation (Lectures 2–3):** Strict Pydantic models validate incoming queries and format outgoing replies. `dispatch_tool` defensively parses raw JSON arguments, handling malformed payloads without crashing.
- **Family 2 — Hybrid Retrieval / RAG with Citations (Lectures 6–8):** Combines lexical **Okapi BM25** with a **Thai Subword Character 3/4-gram & Semantic Concept Vectorizer** fused via **Reciprocal Rank Fusion (RRF, $k=60$)**. Citations `[filename.md # Section]` are injected into every retrieved chunk and parsed into interactive badges.
- **Family 3 — Quantitative Evaluation Benchmark (Lectures 8–9):** 30 curated test cases (`eval/benchmark_data.json`) evaluated across `Recall@1`, `Recall@3`, `Recall@5`, and `MRR` comparing the baseline against improved hybrid RAG, plus Guarded SQL accuracy.
- **Family 4 — ReAct Agent Loop with Tools (Lectures 10 & 13):** Multi-turn autonomous tool-calling loop (`max_steps=5`) with automatic stop condition, error reflection, and guaranteed non-empty Thai synthesis.
- **Family 5 — Guarded Text-to-SQL Execution (Lecture 11):** Dynamic schema prompting directly from `sqlite_master` with 5-layer SQL guards blocking non-SELECT queries, SQL injection, comments, and enforcing `LIMIT 100`.
- **Family 6 — Served Interface (Lectures 4–5):** FastAPI REST backend serving a responsive, mobile-friendly Neubrutalism web application with real-time tool traces and evaluation tabs.

---

## 3. Quantitative Evaluation Benchmark & Results

### 3.1 Evaluation Methodology & Test Set
The evaluation benchmark consists of **30 curated ground-truth test cases** (`eval/benchmark_data.json`), partitioned into four distinct operational categories:
1. **Unstructured RAG (10 cases, TC-01 to TC-10):** Domain-specific questions on Thai sea fish meat textures, seasonal peak availability, cooking recommendations, and Baan Nam Khem artisanal fishing methods.
2. **Structured SQL (10 cases, TC-11 to TC-20):** Exact quantitative questions on seafood pricing, inventory levels, order tracking, and freshness warranty claims.
3. **Compound Multi-Hop (5 cases, TC-21 to TC-25):** Complex questions requiring both document retrieval and relational SQL execution in a single agent turn.
4. **Conversational Chit-Chat (5 cases, TC-26 to TC-30):** Greetings and polite closures to verify the agent skips unnecessary retrieval.

### 3.2 Evaluation Metrics
- **Recall@K ($K \in \{1, 3, 5\}$):** Whether at least one gold chunk is present in the top-$K$ retrieved candidates.
- **Mean Reciprocal Rank (MRR):** $\frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$, measuring ranking quality where $\text{rank}_i$ is the position of the first relevant chunk.
- **Guarded SQL Execution Accuracy:** Percentage of gold queries that pass all 5 security guard layers and execute successfully against `store.db`.

### 3.3 Benchmark Results Table

| Evaluation Metric | Baseline (Naive BM25 Only) | Improved (Hybrid RAG + RRF) | Absolute Delta | Relative Gain |
| :--- | :---: | :---: | :---: | :---: |
| **Recall@1 (Top-1 Accuracy)** | `80.00%` | **`90.00%`** | `+10.00%` | **`+12.5%` lift** |
| **Recall@3** | `100.00%` | **`100.00%`** | `0.00%` | `100% Coverage` |
| **Recall@5** | `100.00%` | **`100.00%`** | `0.00%` | `100% Coverage` |
| **MRR (Mean Reciprocal Rank)** | `0.8833` | **`0.9500`** | `+0.0667` | **`+7.5%` lift** |
| **Guarded SQL Accuracy** | N/A | **`100.00%` (10/10)** | — | **Zero security leaks** |

Every metric in this table is directly reproducible by executing `python evaluate.py`.

---

## 4. Failure Case Analysis & Engineering Defenses

### 4.1 Failure Case 1: Unspaced Thai Compound & Synonym Mismatch (`TC-03`)
- **Query:** *"อยากหาปลาทะเลให้เด็กและคนแก่ทาน ควรเลือกปลาชนิดไหนที่เนื้อนิ่มเคี้ยวง่ายและก้างน้อย?"*
- **Baseline Observation:** Standard lexical BM25 failed to place the gold document (`chk_008` in `snapper_and_emperor.md`) at Rank 1. Because Thai script is written without spaces between words, standard tokenization failed on compound phrases (`ปลาทะเลให้เด็กและคนแก่ทาน`), and the colloquial phrase `"คนแก่"` did not match the formal term `"ผู้สูงอายุ"` used in the corpus.
- **Engineering Fix:** Our Hybrid RAG integrates Thai subword character 3/4-grams and domain synonym expansion (`คนแก่` $\to$ `ผู้สูงอายุ`, `ชาวเล` $\to$ `มอแกลน`). Fused via Reciprocal Rank Fusion ($k=60$), `chk_008` (ปลาเหลืองญี่ปุ่น) achieved Rank 1, lifting Recall@1 from 80% to 90%.

### 4.2 Failure Case 2: Empty Assistant Message on Final Agent Step
- **Observation:** Under multi-turn tool calling, smaller instruction models (`gemma-4-E4B-it`) occasionally emit tool calls, receive the tool result, and then finish the conversation with an empty `message.content` string.
- **Engineering Fix:** In `src/agent.py`, a safety backstop detects if `reply_text` is empty after tool execution. If so, it invokes a forced summary completion with `tool_choice="none"`. If upstream fails, a curated Thai fallback ensures the user is never left with a blank bubble.

### 4.3 Failure Case 3: Hostile SQL Injection & Malicious Payloads
- **Observation:** If a user submits destructive prompts such as *"ลบตาราง orders ทิ้งเดี๋ยวนี้ (DROP TABLE orders)"* or attempts SQL comment injection (`SELECT * FROM orders -- DROP TABLE x`), an unguarded Text-to-SQL system would risk severe data corruption.
- **Engineering Fix:** In accordance with Lecture 11, `guard_sql` enforces 5 independent security layers:
  1. Strips Markdown fences and stray backticks.
  2. Blocks comments (`--`, `/* */`).
  3. Enforces leading `SELECT` or read-only `WITH` CTE statements.
  4. Disallows stacked queries (`;`) and banned keywords (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `PRAGMA`, `ATTACH`, etc.).
  5. Appends `LIMIT 100` automatically. Tested against Lecture 11's 7 hostile probes with 100% rejection.

---

## 5. Limitations & Future Work

While CatEatFish AI delivers robust performance across all 6 capability families, several production limitations remain:
1. **Cold-Chain Inventory Real-Time Sync:** Currently, `store.db` relies on local SQLite. In a commercial deployment, this must be integrated with an enterprise inventory API (e.g., PostgreSQL / ERP webhooks) with row-level locking to handle concurrent customer orders.
2. **Dense Neural Embeddings at Scale:** The pure-Python Thai subword vectorizer and BM25 engine achieve remarkable speed with zero dependencies for our 15-chunk corpus. However, scaling to thousands of multi-page manuals will require dense embedding models (such as `bge-m3`) coupled with a dedicated vector database (e.g., Qdrant or Milvus).
3. **Voice & Multimodal Interface:** Artisanal fishers and busy restaurant kitchen staff frequently work with wet hands. Future enhancements will add Speech-to-Text (Whisper) and fish image identification (Vision-RAG) to allow chefs to snap a photo of a fish catch to receive instant culinary and cooking instructions.

---
*Report submitted in partial fulfillment of the requirements for Capstone Project, Building LLM-Powered Applications, KMITL.*
