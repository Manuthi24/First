from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "faqs.json"
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9']+")
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "to", "for", "of", "and",
    "or", "in", "on", "at", "with", "do", "does", "did", "how", "what", "when",
    "i", "my", "we", "you", "your", "can"
}


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=5)


class RetrievedFAQ(BaseModel):
    id: str
    question: str
    category: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[RetrievedFAQ]
    fallback: bool


class FAQItem(BaseModel):
    id: str
    category: str
    question: str
    answer: str


class FAQIndex:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.items: list[FAQItem] = []
        self.item_vectors: list[Counter[str]] = []
        self.reload()

    def reload(self) -> None:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.items = [FAQItem(**item) for item in payload]
        self.item_vectors = [self._text_vector(item.question) for item in self.items]

    def _tokenize(self, text: str) -> list[str]:
        tokens = [t.lower() for t in TOKEN_PATTERN.findall(text)]
        return [t for t in tokens if t not in STOP_WORDS]

    def _text_vector(self, text: str) -> Counter[str]:
        return Counter(self._tokenize(text))

    @staticmethod
    def _cosine_similarity(a: Counter[str], b: Counter[str]) -> float:
        if not a or not b:
            return 0.0
        shared = set(a.keys()) & set(b.keys())
        dot = sum(a[t] * b[t] for t in shared)
        mag_a = math.sqrt(sum(v * v for v in a.values()))
        mag_b = math.sqrt(sum(v * v for v in b.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        qv = self._text_vector(query)
        scored = []
        for item, item_vec in zip(self.items, self.item_vectors, strict=True):
            score = self._cosine_similarity(qv, item_vec)
            scored.append({"item": item, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


app = FastAPI(title="Customer Support Copilot API", version="1.0.0")
index = FAQIndex(DATA_PATH)
CONFIDENCE_THRESHOLD = 0.2


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/admin/reload")
def admin_reload() -> dict[str, str]:
    index.reload()
    return {"status": "reloaded"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    query = payload.message.strip()
    if not query:
        raise HTTPException(status_code=400, detail="message cannot be empty")

    results = index.search(query, top_k=payload.top_k)
    best = results[0] if results else None

    if not best or best["score"] < CONFIDENCE_THRESHOLD:
        return ChatResponse(
            answer=(
                "I’m not fully confident about that yet. Please share your order ID or contact support@example.com "
                "for help from a human agent."
            ),
            confidence=0.0,
            sources=[],
            fallback=True,
        )

    top_item: FAQItem = best["item"]
    confidence = round(float(best["score"]), 3)

    sources = [
        RetrievedFAQ(
            id=r["item"].id,
            question=r["item"].question,
            category=r["item"].category,
            score=round(float(r["score"]), 3),
        )
        for r in results
    ]

    answer = (
        f"{top_item.answer}\n\n"
        f"Source: {top_item.question}"
    )

    return ChatResponse(answer=answer, confidence=confidence, sources=sources, fallback=False)
