import json
from pathlib import Path

from pydantic import TypeAdapter

from services.vector_store.embeddings import cosine_similarity, embed_text
from shared.schemas.feedback import FeedbackRecord
from shared.schemas.sources import VectorSearchHit


class LocalVectorStore:
    def __init__(self, path: str = "data/vector_store.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._records = {}
            return
        self._records = json.loads(self.path.read_text())

    def persist(self) -> None:
        self.path.write_text(json.dumps(self._records, indent=2, sort_keys=True))

    def upsert_feedback(self, records: list[FeedbackRecord]) -> int:
        for record in records:
            text = vector_text(record)
            self._records[record.id] = {
                "id": record.id,
                "embedding": embed_text(text),
                "text": record.cleaned_text,
                "source": record.source,
                "source_url": str(record.source_url),
                "public_author_name": record.public_author_name,
                "public_author_url": str(record.public_author_url)
                if record.public_author_url
                else None,
                "public_author_note": record.public_author_note,
                "company": record.analysis.company,
                "product": record.analysis.product,
                "topics": record.analysis.topics,
                "sentiment_score": record.analysis.sentiment_score,
                "published_at": record.published_at.isoformat(),
            }
        self.persist()
        return len(records)

    def search(
        self,
        query: str,
        *,
        company: str | None = None,
        source: str | None = None,
        limit: int = 5,
    ) -> list[VectorSearchHit]:
        query_embedding = embed_text(query)
        scored = []
        for payload in self._records.values():
            if company and payload["company"] != company:
                continue
            if source and payload["source"] != source:
                continue
            score = cosine_similarity(query_embedding, payload["embedding"])
            scored.append((score, payload))

        adapter = TypeAdapter(VectorSearchHit)
        return [
            adapter.validate_python({"score": score, **payload})
            for score, payload in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]
        ]

    def count(self) -> int:
        return len(self._records)


def vector_text(record: FeedbackRecord) -> str:
    return " ".join(
        [
            record.cleaned_text,
            record.analysis.summary,
            record.analysis.company,
            record.analysis.product or "",
            " ".join(record.analysis.topics),
            record.location or "",
        ]
    )
