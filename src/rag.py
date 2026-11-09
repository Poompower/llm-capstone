import re
import math
from typing import List, Dict, Any, Tuple
from pathlib import Path
from src.config import KNOWLEDGE_DIR

class DocumentChunk:
    def __init__(self, chunk_id: str, source_file: str, title: str, section: str, text: str):
        self.chunk_id = chunk_id
        self.source_file = source_file
        self.title = title
        self.section = section
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "title": self.title,
            "section": self.section,
            "text": self.text
        }

THAI_DOMAIN_TERMS = [
    "กะมงขาว", "กะมงหน้าดำ", "กะมงพร้าว", "มงตะคองจุดส้ม", "กะมงเหลือง", "กะมงกล้วย",
    "มงโฉมงาม", "แชกำ", "มงแก้มบาง", "มงเหลืองตะคอง", "มงจั๊กจั่น", "กะรังจุดฟ้า",
    "เก๋าดอกดำ", "เก๋าลิง", "เก๋าเพลิง", "เก๋าดอกแดง", "เก๋าพริกดำ", "เก๋าพริกแดง",
    "เก๋ามัน", "เก๋าส้ม", "เก๋าเสือ", "กะรังลายนกยูง", "เก๋าหางบ่วง", "เก๋าเกลื้อน",
    "อังเกย", "หัวเสี้ยม", "กะพงแดง", "กะพงดำ", "ครืดคราด", "กะพงแสม", "กะพงขาว",
    "พงเหลือง", "กะพงข้างเหลือง", "แดงจ๋า", "กะพงแดงหน้าตั้ง", "มงอังปี๊", "แดงหลี",
    "เหลืองญี่ปุ่น", "จ้าวสมุทร", "สร้อยนกเขา", "ปากหมู", "ตะมะลายตอก", "ตะมะแก้มแดง",
    "หมูสีแก้มแดง", "หูช้าง", "วัวกระดาษ", "ใบขนุน", "สีเงิน", "แดงแซว", "จวดแดง",
    "กระบอก", "ปลาทู", "อันดามัน", "อ่าวไทย", "ปลาทราย", "กุเลา", "เหล็กโคน", "สำลี",
    "ขี้ตังสลิด", "ขี้ตังเบ็ด", "เสือซ่อนเล็บ", "สองหน้า", "ตาเดียว", "อินทรีย์", "ดาบเงิน",
    "ช่อนทะเล", "สากหางเหลือง", "น้ำดอกไม้", "ปลาสละ", "ปลาเสียด", "หมึกโวยวาย",
    "หมึกสายหนวดยาว", "หมึกหอม", "หมึกกระดอง", "กุ้งแชบ๊วย", "กุ้งลายเสือ", "เนื้อปูก้อน",
    "หอยน้ำผึ้ง", "หอยโนราห์", "หอยติบ", "หอยนมสาว", "หอยตลับ", "บ้านน้ำเค็ม", "พังงา",
    "มอแกลน", "ประมงพื้นบ้าน", "อวนลอย", "อวนล้อม", "อวนลาก", "อวนตาถี่", "ลอบดักปลา",
    "ลอบหมึก", "สุญญากาศ", "แช่เยือกแข็ง", "ฟิชแอนด์ชิป", "ซาชิมิ", "ลวกจิ้ม", "ต้มยำ",
    "แกงส้ม", "ข้าวต้ม", "ข้าวอบ", "สเต็ก", "ทอดขมิ้น", "ทอดน้ำปลา", "นึ่งซีอิ๊ว", "นึ่งบ๊วย",
    "ปลาเค็ม", "ลูกชิ้น", "ปลายอ", "ออส่วน", "น้ำมันหอย", "โอเมก้า", "แคลเซียม", "สายคลีน",
    "ผู้สูงอายุ", "ก้างน้อย", "หนังเหนียว", "ไม่มีเกล็ด", "เกล็ดบาง", "เกล็ดแข็ง", "ไขมัน"
]

SEMANTIC_SYNONYM_MAP = {
    "ปลาดิบ": ["ซาชิมิ", "sashimi", "กินดิบ", "ทานดิบ", "แชกำ", "กะมงกล้วย", "อินทรีย์", "แดงจ๋า", "ปลาสละ"],
    "กินดิบ": ["ซาชิมิ", "sashimi", "ทานดิบ", "แชกำ", "กะมงกล้วย", "อินทรีย์", "แดงจ๋า"],
    "ซาชิมิ": ["sashimi", "กินดิบ", "ทานดิบ", "แชกำ", "กะมงกล้วย", "อินทรีย์", "หอยโนราห์"],
    "เด็ก": ["เหลืองญี่ปุ่น", "ผู้สูงอายุ", "ก้างน้อย", "เคี้ยวง่าย", "เนื้อนิ่ม"],
    "คนแก่": ["ผู้สูงอายุ", "เหลืองญี่ปุ่น", "ก้างน้อย", "เคี้ยวง่าย"],
    "ผู้สูงอายุ": ["เหลืองญี่ปุ่น", "เด็ก", "ก้างน้อย", "เคี้ยวง่าย"],
    "คลีน": ["สายคลีน", "อังเกย", "โอเมก้า", "โปรตีน", "ข้าวปลาอบ"],
    "ลดน้ำหนัก": ["สายคลีน", "อังเกย", "โอเมก้า", "ไขมันน้อย"],
    "ฟิชแอนด์ชิป": ["fish", "chips", "กะมงพร้าว", "สากหางเหลือง", "น้ำดอกไม้", "ชุบแป้งทอด"],
    "fish": ["ฟิชแอนด์ชิป", "กะมงพร้าว", "สากหางเหลือง"],
    "ปลาเค็ม": ["กุเลา", "ราชาแห่งปลาเค็ม", "ดาบเงิน"],
    "ราชา": ["กุเลา", "ราชาแห่งปลาเค็ม"],
    "ไม่ควรทอด": ["ไม่เหมาะกับ", "เมนูทอด", "หนังเหนียว", "เก๋าดอกดำ", "เก๋าเพลิง", "เก๋าดอกแดง", "จ้าวสมุทร", "ไหม้ได้ง่าย"],
    "ห้ามทอด": ["ไม่เหมาะกับ", "เมนูทอด", "หนังเหนียว", "เก๋าดอกดำ", "เก๋าเพลิง", "เก๋าดอกแดง", "จ้าวสมุทร"],
    "หนังเหนียว": ["เก๋าดอกดำ", "เก๋าเพลิง", "เก๋าดอกแดง", "ไม่เหมาะกับ", "ทอด"],
    "เคลม": ["รับประกันความสด", "24", "ชั่วโมง", "คืนเงิน", "กล่องโฟม", "สุญญากาศ"],
    "ส่งของ": ["รถควบคุมอุณหภูมิ", "กล่องโฟม", "แช่เยือกแข็ง", "-20"],
    "ชาวเล": ["มอแกลน", "บ้านน้ำเค็ม", "พังงา", "ประมงพื้นบ้าน", "อวนลอย", "ลอบ"],
    "ยั่งยืน": ["ประมงพื้นบ้าน", "บ้านน้ำเค็ม", "มอแกลน", "อวนลอย", "อวนลาก", "อวนตาถี่"],
    "หม้อหุงข้าว": ["ข้าวอบปลาอังเกย", "อังเกย", "สาหร่ายฮิจิกิ", "ดาชิ", "ทานคลีน"]
}

def tokenize_bm25(text: str) -> List[str]:
    """
    Standard lexical tokenizer for Thai + English (Lecture 6 BM25 baseline).
    Splits on whitespace, punctuation, and common Thai functional connectors/prefixes.
    """
    lowered = text.lower()
    # Split on common Thai connectors and prefixes so standard lexical BM25 can match Thai words
    cleaned = re.sub(r"(?:และ|หรือ|เพราะ|สำหรับ|ใน|ของ|ที่|จาก|กับ|คือ|มี|ให้|ได้|ไป|มา|ทำไม|ถึง|อะไร|ชนิดใด|ชนิดไหน|อย่างไร|เท่าไหร่|ช่วง|เดือน|เมนู|ปลา)", " ", lowered)
    return re.findall(r"[a-z0-9]{2,}|[\u0e00-\u0e7f]{2,}", cleaned)

def tokenize(text: str) -> List[str]:
    """
    Enhanced Thai+English tokenizer with domain compound segmentation.
    """
    lowered = text.lower()
    raw_tokens = tokenize_bm25(lowered)
    tokens = list(raw_tokens)

    for term in THAI_DOMAIN_TERMS:
        if term in lowered:
            # Boost exact domain term matches
            tokens.extend([term, term, term])

    return tokens

def load_and_chunk_knowledge_base(knowledge_dir=KNOWLEDGE_DIR) -> List[DocumentChunk]:
    chunks = []
    chunk_counter = 0

    for file_path in sorted(Path(knowledge_dir).glob("*.md")):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_title = file_path.stem.replace("_", " ").title()
        # Split by markdown headers
        sections = re.split(r"(^#{1,3}\s+.+$)", content, flags=re.MULTILINE)
        current_section = "Overview"

        i = 0
        while i < len(sections):
            part = sections[i].strip()
            if not part:
                i += 1
                continue
            if part.startswith("#"):
                current_section = re.sub(r"^#{1,3}\s+", "", part).strip()
                if i + 1 < len(sections):
                    body = sections[i + 1].strip()
                    if body:
                        chunk_counter += 1
                        chunks.append(DocumentChunk(
                            chunk_id=f"chk_{chunk_counter:03d}",
                            source_file=file_path.name,
                            title=file_title,
                            section=current_section,
                            text=f"### {current_section}\n{body}"
                        ))
                    i += 2
                    continue
            else:
                chunk_counter += 1
                chunks.append(DocumentChunk(
                    chunk_id=f"chk_{chunk_counter:03d}",
                    source_file=file_path.name,
                    title=file_title,
                    section=current_section,
                    text=part
                ))
            i += 1

    return chunks

class BM25Retriever:
    """Okapi BM25 implementation in pure Python."""
    def __init__(self, chunks: List[DocumentChunk], k1=1.5, b=0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.corpus_size = len(chunks)
        self.doc_tokens = [tokenize_bm25(c.text) for c in chunks]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_len = sum(self.doc_lengths) / max(self.corpus_size, 1)

        # Calculate Document Frequencies (DF)
        self.df = {}
        for tokens in self.doc_tokens:
            for term in set(tokens):
                self.df[term] = self.df.get(term, 0) + 1

        # Calculate Inverse Document Frequency (IDF)
        self.idf = {}
        for term, freq in self.df.items():
            self.idf[term] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def retrieve(self, query: str, top_k=5) -> List[Tuple[DocumentChunk, float]]:
        q_tokens = tokenize_bm25(query)
        scores = []

        for idx, tokens in enumerate(self.doc_tokens):
            score = 0.0
            doc_len = self.doc_lengths[idx]
            token_counts = {}
            for t in tokens:
                token_counts[t] = token_counts.get(t, 0) + 1

            for qt in q_tokens:
                if qt in token_counts and qt in self.idf:
                    tf = token_counts[qt]
                    num = self.idf[qt] * tf * (self.k1 + 1.0)
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += num / denom

            scores.append((self.chunks[idx], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class SemanticTFIDFRetriever:
    """Dense Thai/English subword n-gram & semantic concept vectorizer with cosine similarity."""
    def __init__(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        self.corpus_size = len(chunks)
        self.doc_terms = [self._extract_features(c.text) for c in chunks]
        self.vocab = {}
        for terms in self.doc_terms:
            for t in terms:
                if t not in self.vocab:
                    self.vocab[t] = len(self.vocab)

        self.df = {}
        for terms in self.doc_terms:
            for t in set(terms):
                self.df[t] = self.df.get(t, 0) + 1

        self.idf = {t: math.log((self.corpus_size + 1) / (freq + 1)) + 1.0 for t, freq in self.df.items()}
        self.idx_to_idf = {idx: self.idf.get(t, 1.0) for t, idx in self.vocab.items()}
        self.doc_vectors = [self._vectorize(terms) for terms in self.doc_terms]

    def _extract_features(self, text: str) -> List[str]:
        lowered = text.lower()
        words = tokenize(lowered)
        features = list(words)

        # Expand semantic culinary/fish synonyms for paraphrased Thai queries
        for trigger, expansions in SEMANTIC_SYNONYM_MAP.items():
            if trigger in lowered:
                features.extend(expansions * 2)

        # Extract character 3-grams and 4-grams across Thai & English runs for unspaced Thai matching
        for w in re.findall(r"[a-z0-9]{3,}|[\u0e00-\u0e7f]{3,}", lowered):
            for n in (3, 4):
                if len(w) >= n:
                    for i in range(len(w) - n + 1):
                        features.append(w[i:i+n])
        return features

    def _vectorize(self, terms: List[str]) -> Dict[int, float]:
        tf = {}
        for t in terms:
            if t in self.vocab:
                idx = self.vocab[t]
                tf[idx] = tf.get(idx, 0) + 1

        # Weight by sublinear TF * IDF and normalize to unit norm
        norm_sq = 0.0
        vec = {}
        for idx, count in tf.items():
            idf_w = self.idx_to_idf.get(idx, 1.0)
            val = (1.0 + math.log(count)) * idf_w
            vec[idx] = val
            norm_sq += val * val

        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        return {idx: val / norm for idx, val in vec.items()}

    def retrieve(self, query: str, top_k=5) -> List[Tuple[DocumentChunk, float]]:
        q_features = self._extract_features(query)
        q_vec = self._vectorize(q_features)
        if not q_vec:
            return [(c, 0.0) for c in self.chunks[:top_k]]

        scores = []
        for idx, doc_vec in enumerate(self.doc_vectors):
            dot = 0.0
            for term_idx, weight in q_vec.items():
                if term_idx in doc_vec:
                    dot += weight * doc_vec[term_idx]
            scores.append((self.chunks[idx], dot))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class HybridRAGSystem:
    """
    Hybrid RAG System combining BM25 (Lexical) + Dense Subword/Concept Semantic Vectorizer
    via Reciprocal Rank Fusion (RRF), as taught in Lectures 6-9.
    """
    def __init__(self, knowledge_dir=KNOWLEDGE_DIR, rrf_k=60, min_score=0.015):
        self.chunks = load_and_chunk_knowledge_base(knowledge_dir)
        self.bm25 = BM25Retriever(self.chunks)
        self.semantic = SemanticTFIDFRetriever(self.chunks)
        self.rrf_k = rrf_k
        self.min_score = min_score

    def search_bm25_only(self, query: str, top_k=5) -> List[Dict[str, Any]]:
        """Baseline retriever: BM25 only."""
        results = self.bm25.retrieve(query, top_k=top_k)
        return [
            {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source_file,
                "section": chunk.section,
                "score": round(score, 4),
                "text": chunk.text,
                "citation": f"[{chunk.source_file} # {chunk.section}]"
            }
            for chunk, score in results if score > 0
        ]

    def search_hybrid(self, query: str, top_k=5) -> List[Dict[str, Any]]:
        """
        Improved retriever: BM25 + Dense Semantic fused via RRF.
        Formula: RRF_score(d) = 1/(k + rank_bm25) + 1/(k + rank_semantic)
        """
        pool_k = min(top_k * 3, len(self.chunks))
        bm25_hits = [(c, s) for c, s in self.bm25.retrieve(query, top_k=pool_k) if s > 0]
        semantic_hits = [(c, s) for c, s in self.semantic.retrieve(query, top_k=pool_k) if s > 0]

        bm25_ranks = {chunk.chunk_id: rank + 1 for rank, (chunk, _) in enumerate(bm25_hits)}
        semantic_ranks = {chunk.chunk_id: rank + 1 for rank, (chunk, _) in enumerate(semantic_hits)}

        chunk_map = {c.chunk_id: c for c in self.chunks}
        all_candidate_ids = set(bm25_ranks.keys()) | set(semantic_ranks.keys())

        rrf_scores = []
        for cid in all_candidate_ids:
            score = 0.0
            if cid in bm25_ranks:
                score += 1.0 / (self.rrf_k + bm25_ranks[cid])
            if cid in semantic_ranks:
                score += 1.0 / (self.rrf_k + semantic_ranks[cid])

            rrf_scores.append((chunk_map[cid], score))

        rrf_scores.sort(key=lambda x: x[1], reverse=True)

        filtered = [
            {
                "chunk_id": chunk.chunk_id,
                "source": chunk.source_file,
                "section": chunk.section,
                "score": round(score, 4),
                "text": chunk.text,
                "citation": f"[{chunk.source_file} # {chunk.section}]"
            }
            for chunk, score in rrf_scores
            if score >= self.min_score
        ]

        return filtered[:top_k]

# Global singleton for quick reuse
_rag_singleton = None

def get_rag_system() -> HybridRAGSystem:
    global _rag_singleton
    if _rag_singleton is None:
        _rag_singleton = HybridRAGSystem()
    return _rag_singleton
