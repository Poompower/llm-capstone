# CatEatFish AI: สถาปัตยกรรม ReAct Agent ร่วมกับ Hybrid RAG และ Guarded Text-to-SQL สำหรับอาหารทะเลไทยและการจัดการประมงพื้นบ้าน
**หลักสูตร:** Building LLM-Powered Applications (KMITL) — Capstone Project  
**ผู้พัฒนาโครงงาน:** พงศธร กิจเจตน์นี (Pongsatorn Kitjetnee)  
**คลังโค้ด GitHub:** [https://github.com/Poompower/llm-capstone](https://github.com/Poompower/llm-capstone)  
**ระบบที่เผยแพร่จริง (Render):** [https://cateatfish-ai.onrender.com](https://cateatfish-ai.onrender.com)  
**โมเดลหลักที่ใช้:** `gemma-4-E4B-it` ผ่าน Course Proxy (`https://llm.nat-d.uk/v1`)  
**แหล่งข้อมูลคลังความรู้:** CAT EAT FISH (แมวกินปลา) — ประมงพื้นบ้านบ้านน้ำเค็ม จ.พังงา (`cateatfish.co/sea/thai-fish`)  

---

## ข้อค้นพบสำคัญ (Key Findings & Executive Summary)
- **Hybrid RAG เหนือกว่า Naive BM25 ชัดเจน:** การผสานคำค้นหา Okapi BM25 เข้ากับ Subword 3/4-grams และ Semantic Synonyms ผ่านสูตร Reciprocal Rank Fusion (RRF, $k=60$) ช่วยยกระดับความแม่นยำในการดึงข้อมูลอันดับแรก (Recall@1) จาก **80.00% ขึ้นสู่ 90.00% (+12.5% relative lift)** และเพิ่มค่า MRR จาก **0.8833 สู่ 0.9500 (+7.5%)**
- **แก้ปัญหาคำไทยเขียนติดกันและภาษาพูด:** ระบบค้นหาแบบดั้งเดิมล้มเหลวเมื่อผู้ใช้ถามด้วยคำพูดทั่วไป เช่น `"คนแก่"` (ไม่ตรงกับ `"ผู้สูงอายุ"` ในเอกสาร) หรือพิมพ์คำติดกัน `"ปลาทะเลให้เด็กและคนแก่ทาน"` โดย Hybrid RAG แก้ไขปัญหานี้ได้อย่างแม่นยำ (TC-03 พลิกกลับมาเป็น Rank 1)
- **ความปลอดภัยระบบฐานข้อมูล 100%:** ระบบ Guarded Text-to-SQL (Lecture 11) สกัดกั้นคำสั่งอันตราย (DROP, DELETE, Injection, Comments) ได้ 100% เต็มจากการทดสอบ 7 Hostile Probes และรันคำสั่ง SELECT อ่านข้อมูลยอดขาย/สต็อกสำเร็จ 10/10 เคส
- **ReAct Agent ทำงานอย่างมีขอบเขต:** กำหนด `max_steps=5` ป้องกันลูปไม่สิ้นสุด พร้อมระบบสกัดคำตอบว่างเปล่า (Empty Response Fallback) รับประกันการตอบสรุปภาษาไทยที่มีหลักฐานอ้างอิงเสมอ

---

## 1. ปัญหาและกลุ่มผู้ใช้งาน (Problem Statement & Target Audience)
### 1.1 ปัญหาภาพหลอนและความเข้าใจผิดเรื่องปลาทะเลไทยใน LLM ทั่วไป
น่านน้ำทะเลอันดามันและอ่าวไทยมีความหลากหลายทางชีวภาพสูงมาก มีปลาทะเลที่กินได้มากกว่า 40 ชนิด ซึ่งจับโดยชาวประมงพื้นบ้านบ้านน้ำเค็มและชาวมอแกลน จ.พังงา ด้วยเครื่องมือเลือกสรร เช่น `อวนลอย` และ `ลอบดักปลา` ที่ไม่ทำลายแนวปะการัง และทำการเก็บรักษาด้วยระบบแช่เยือกแข็ง `-20°C` ทันทีที่ขึ้นจากเรือ อย่างไรก็ตาม ในปัจจุบันพบปัญหาสำคัญ:
- การปรุงอาหารผิดวิธีจนเสียรสชาติ (Culinary Mispreparation): เช่น นำปลาเก๋าหนังหนา (เก๋าดอกดำ, เก๋าเพลิง) ไปทอด หนังจะเหนียวและกระด้างจนรับประทานไม่ได้ หรือนำปลาจ้าวสมุทรที่มีไขมันสูงไปทอด เนื้อจะไหม้ง่าย
- ความต้องการข้อมูลผสมผสาน (Hybrid Intent): ลูกค้าต้องการคำตอบทั้งมิติความรู้เชิงอาหารและมิติเชิงพาณิชย์พร้อมกัน เช่น *"ปลาแชกำเหมาะกินดิบไหม ราคาแพคละเท่าไหร่ และในสต็อกเหลือกี่แพค?"*

### 1.2 กลุ่มเป้าหมายผู้ใช้งาน (Target Audience)
1. ผู้บริโภคและแม่บ้านสายสุขภาพ
2. เชฟและร้านอาหาร
3. ลูกค้าและฝ่ายบริการลูกค้าของร้าน CAT EAT FISH

---

## 2. การออกแบบระบบและสถาปัตยกรรม (System Architecture & Design)
ครอบคลุม 6 กลุ่มความสามารถ (Capability Families) ตามเกณฑ์รายวิชา:
1. **Structured Output & Schema Validation:** Pydantic models (`ChatRequest`, `ChatResponse`)
2. **Hybrid RAG with Injected Citations:** Okapi BM25 + Subword 3/4-grams + Semantic Synonyms ผ่าน RRF ($k=60$)
3. **Quantitative Retrieval Evaluation:** ชุดทดสอบ 30 ข้อใน `eval/benchmark_data.json`
4. **ReAct Agent Loop with Tools:** Native Tool Calling loop (`max_steps=5`)
5. **Guarded Text-to-SQL Execution:** Live DDL จาก `sqlite_master` พร้อมกำแพงความปลอดภัย 5 ชั้น (Lecture 11)
6. **Served Full-Stack Interface:** FastAPI REST Backend + Retro Neubrutalism Web UI

---

## 3. ระเบียบวิธีการประเมินผลเชิงปริมาณ (Evaluation Methodology)
- ชุดทดสอบ 30 ข้อ: RAG 10 ข้อ, SQL 10 ข้อ, Multi-Hop 5 ข้อ, Chit-Chat 5 ข้อ
- เมตริก: Recall@1, Recall@3, Recall@5, MRR, Guarded SQL Accuracy

| เมทริกซ์ชี้วัด (Metric) | Baseline (Naive BM25) | Improved (Hybrid RAG) | ผลการเปลี่ยนแปลง (Lift / Gain) |
| :--- | :---: | :---: | :---: |
| **Recall@1 (Top-1 Accuracy)** | `80.00%` (8/10) | **`90.00%` (9/10)** | **+10.00% สุทธิ (+12.5% Relative Lift)** |
| **Recall@3** | `100.00%` (10/10) | **`100.00%` (10/10)** | 100.00% (ครอบคลุมสมบูรณ์) |
| **Recall@5** | `100.00%` (10/10) | **`100.00%` (10/10)** | 100.00% (ครอบคลุมสมบูรณ์) |
| **MRR (Mean Reciprocal Rank)** | `0.8833` | **`0.9500`** | **+0.0667 สุทธิ (+7.5% Ranking Boost)** |
| **Guarded SQL Accuracy** | N/A | **`100.00%` (10/10)** | ผ่านการทดสอบความปลอดภัยครบถ้วน |

---

## 4. ผลการทดลองและการวิเคราะห์ความผิดพลาดอย่างตรงไปตรงมา (Honest Analysis)
- **กรณีศึกษาที่ 1 (TC-03):** วลีคำติดกันในภาษาไทย `ให้เด็กและคนแก่ทาน` และคำพ้อง `คนแก่` vs `ผู้สูงอายุ` -> แก้ไขด้วย Subword 3/4-grams และ Semantic Synonym Map ทำให้ `chk_008` (ปลาเหลืองญี่ปุ่น) พลิกขึ้นเป็น Rank 1
- **กรณีศึกษาที่ 2 (TC-06):** คำว่า `ชาวเล` vs `ชาวมอแกลน` ในบทความประมงพื้นบ้านบ้านน้ำเค็ม -> แก้ไขด้วย Synonym Concept Expansion
- **กรณีศึกษาที่ 3:** โมเดลคืนค่าข้อความว่างเปล่า (Empty Assistant Message) -> บังคับ `tool_choice="none"` สรุปคำตอบภาษาไทย
- **กรณีศึกษาที่ 4:** การสกัดกั้นการเจาะระบบ (7 Hostile Probes) ตาม Lecture 11 -> สกัดกั้นสำเร็จ 100%

---

## 5. ข้อจำกัดและแผนงานในอนาคต (Limitations & Future Roadmap)
- ข้อจำกัด: การล็อคไฟล์ของ SQLite เมื่อมีผู้ใช้งานพร้อมกันสูง, การสเกลเวกเตอร์เมื่อเอกสารเพิ่มเป็นหลักหมื่นหน้า
- แผนพัฒนา: Multimodal Vision RAG ถ่ายรูปปลา, Voice Agent แปลงเสียงพูดในครัว, การเชื่อมต่อ Telemetry รถห้องเย็นจริง
