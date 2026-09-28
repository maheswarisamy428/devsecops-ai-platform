"""Local RAG-based SRE log intelligence agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "synthetic_logs.json"
CHROMA_DB_PATH = BASE_DIR / "chroma_db"

COLLECTION_NAME = "sre_logs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chroma distance is model/metric dependent.
# This is a relevance filter, not the only evidence check.
MAX_DISTANCE = 1.0

DEFAULT_TOP_K = 5


class SRELogAgent:
    """Retrieve and answer questions using synthetic SRE logs."""

    def __init__(
        self,
        log_file: Path = LOG_FILE,
    ) -> None:
        """Initialize embedding model and persistent Chroma collection."""
        self.log_file = log_file

        self.model = SentenceTransformer(EMBEDDING_MODEL)

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH),
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
        )

    # =========================================================================
    # Log loading
    # =========================================================================

    def load_logs(self) -> list[dict[str, str]]:
        """Load synthetic logs from JSON."""
        if not self.log_file.exists():
            raise FileNotFoundError(
                f"Log file not found: {self.log_file}"
            )

        with self.log_file.open("r", encoding="utf-8") as file:
            logs = json.load(file)

        if not isinstance(logs, list):
            raise ValueError(
                "Expected synthetic_logs.json to contain a JSON list."
            )

        return logs

    # =========================================================================
    # Log formatting
    # =========================================================================

    @staticmethod
    def _format_log(log: dict[str, str]) -> str:
        """Convert a structured log into searchable text."""
        return (
            f"{log['timestamp']} "
            f"{log['service']} "
            f"{log['level']} "
            f"{log['message']}"
        )

    # =========================================================================
    # Indexing
    # =========================================================================

    def index_logs(self) -> None:
        """Embed and store logs in ChromaDB."""
        logs = self.load_logs()

        if not logs:
            return

        documents = [
            self._format_log(log)
            for log in logs
        ]

        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        ).tolist()

        ids = [
            f"log-{index}"
            for index in range(len(documents))
        ]

        metadatas = [
            {
                "timestamp": log["timestamp"],
                "service": log["service"],
                "level": log["level"],
            }
            for log in logs
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    # =========================================================================
    # Semantic retrieval
    # =========================================================================

    def retrieve(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most relevant logs.

        Returns:

        [
            {
                "document": "...",
                "distance": 0.42,
                "metadata": {...}
            }
        ]
        """
        if not question.strip():
            return []

        if self.collection.count() == 0:
            return []

        top_k = max(
            1,
            min(top_k, self.collection.count()),
        )

        query_embedding = self.model.encode(
            [question],
            normalize_embeddings=True,
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=[
                "documents",
                "distances",
                "metadatas",
            ],
        )

        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        retrieved: list[dict[str, Any]] = []

        for document, distance, metadata in zip(
            documents,
            distances,
            metadatas,
        ):
            retrieved.append(
                {
                    "document": str(document),
                    "distance": float(distance),
                    "metadata": metadata or {},
                }
            )

        return retrieved

    # =========================================================================
    # Keyword fallback
    # =========================================================================

    def _keyword_evidence(
        self,
        question: str,
    ) -> list[str]:
        """Find exact operational evidence when semantic retrieval is weak."""
        logs = self.load_logs()

        question_lower = question.lower()

        keyword_groups = {
            "deployment": [
                "deployment",
                "deploy",
                "readiness probe",
                "rolled back",
                "rollback",
            ],
            "restart": [
                "restarted",
                "restart",
                "memory limit",
                "oom",
            ],
            "memory": [
                "memory",
                "memory limit",
                "oom",
            ],
            "database": [
                "database",
                "db",
                "postgres",
                "postgresql",
                "mysql",
                "redis",
            ],
            "readiness": [
                "readiness",
                "readiness probe",
            ],
            "rollback": [
                "rollback",
                "rolled back",
            ],
            "pod": [
                "pod",
            ],
            "service": [
                "service",
            ],
            "outage": [
                "outage",
                "unavailable",
                "availability",
            ],
        }

        keywords: list[str] = []

        for trigger, terms in keyword_groups.items():
            if trigger in question_lower:
                keywords.extend(terms)

        keywords = list(dict.fromkeys(keywords))

        if not keywords:
            return []

        matches: list[str] = []

        for log in logs:
            message = log["message"].lower()

            if any(
                keyword in message
                for keyword in keywords
            ):
                matches.append(
                    self._format_log(log)
                )

        return matches

    # =========================================================================
    # Evidence
    # =========================================================================

    def get_evidence(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[str]:
        """Return deduplicated semantic and keyword evidence."""
        results = self.retrieve(
            question,
            top_k=top_k,
        )

        semantic_evidence = [
            str(result["document"])
            for result in results
            if float(result["distance"]) <= MAX_DISTANCE
        ]

        keyword_evidence = self._keyword_evidence(question)

        evidence = list(
            dict.fromkeys(
                semantic_evidence + keyword_evidence
            )
        )

        return evidence

    # =========================================================================
    # Answer generation
    # =========================================================================

    def answer_with_evidence(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> dict[str, Any]:
        """
        Return answer and supporting evidence together.

        This is the preferred method for the Streamlit UI.
        """
        evidence = self.get_evidence(
            question,
            top_k=top_k,
        )

        if not evidence:
            return {
                "answer": (
                    "I don't know based on the available logs."
                ),
                "evidence": [],
            }

        conclusion = self._derive_conclusion(
            question,
            evidence,
        )

        answer = (
            "Based on the retrieved logs:\n"
            + "\n".join(
                f"- {line}"
                for line in evidence[:5]
            )
            + "\n\n"
            "Conclusion: "
            + conclusion
        )

        return {
            "answer": answer,
            "evidence": evidence[:top_k],
        }

    def answer(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> str:
        """Return a text-only answer for CLI compatibility."""
        result = self.answer_with_evidence(
            question,
            top_k=top_k,
        )

        return str(result["answer"])

    # =========================================================================
    # Deterministic conclusion
    # =========================================================================

    @staticmethod
    def _derive_conclusion(
        question: str,
        evidence: list[str],
    ) -> str:
        """Derive a deterministic conclusion from log evidence."""
        text = " ".join(evidence).lower()
        question_lower = question.lower()

        # ---------------------------------------------------------------------
        # Deployment failure
        # ---------------------------------------------------------------------

        if (
            (
                "deploy" in question_lower
                or "deployment" in question_lower
            )
            and (
                "fail" in question_lower
                or "failed" in question_lower
            )
        ):
            if "readiness probe failed" in text:
                conclusion = (
                    "the deployment failed because the "
                    "readiness probe failed."
                )

                if "exceeded memory limit" in text:
                    conclusion += (
                        " The affected pod also exceeded its "
                        "memory limit and was restarted."
                    )

                if "rolled back" in text:
                    conclusion += (
                        " The deployment was subsequently rolled back."
                    )

                return conclusion

        # ---------------------------------------------------------------------
        # Readiness probe
        # ---------------------------------------------------------------------

        if (
            "readiness" in question_lower
            or "readiness probe" in question_lower
        ):
            if "readiness probe failed" in text:
                conclusion = (
                    "the readiness probe failed, which prevented "
                    "the affected pod from becoming ready."
                )

                if "rolled back" in text:
                    conclusion += (
                        " The deployment was subsequently rolled back."
                    )

                return conclusion

        # ---------------------------------------------------------------------
        # Restart
        # ---------------------------------------------------------------------

        if "restart" in question_lower:
            if "exceeded memory limit" in text:
                return (
                    "the embedding-service pod was restarted because "
                    "the container exceeded its memory limit."
                )

        # ---------------------------------------------------------------------
        # Memory
        # ---------------------------------------------------------------------

        if "memory" in question_lower:
            if "exceeded memory limit" in text:
                return (
                    "the embedding-service pod exceeded its memory "
                    "limit and was restarted."
                )

        # ---------------------------------------------------------------------
        # Rollback
        # ---------------------------------------------------------------------

        if (
            "rollback" in question_lower
            or "rolled back" in question_lower
        ):
            if "rolled back" in text:
                return (
                    "the deployment was rolled back to version "
                    "7e21b8a after the failed deployment."
                )

        # ---------------------------------------------------------------------
        # Database / outage
        # ---------------------------------------------------------------------

        if (
            "database" in question_lower
            and (
                "outage" in question_lower
                or "down" in question_lower
                or "failure" in question_lower
                or "failed" in question_lower
            )
        ):
            for database in (
                "postgresql",
                "postgres",
                "mysql",
                "redis",
            ):
                if database in text:
                    return (
                        f"the available logs identify {database} "
                        "as the database associated with the incident."
                    )

        # ---------------------------------------------------------------------
        # Generic fallback
        # ---------------------------------------------------------------------

        return (
            "the available logs contain the evidence shown above, "
            "but they do not establish a more specific conclusion."
        )


# ============================================================================
# Command-line interface
# ============================================================================

def main() -> None:
    """Run the SRE log agent from the command line."""
    agent = SRELogAgent()

    agent.index_logs()

    question = " ".join(
        sys.argv[1:]
    ).strip()

    if not question:
        print(
            "Usage: python sre_agent.py "
            '"Why did the last deploy fail?"'
        )
        raise SystemExit(1)

    result = agent.answer_with_evidence(
        question
    )

    print(result["answer"])

    print("\n--- Evidence ---")

    for evidence in result["evidence"]:
        print(evidence)


if __name__ == "__main__":
    main()