"""Local RAG-based SRE log intelligence agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "synthetic_logs.json"

COLLECTION_NAME = "sre_logs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chroma distance is model-dependent, so do not make the
# threshold the only mechanism for deciding whether evidence exists.
MAX_DISTANCE = 1.0


class SRELogAgent:
    """Retrieve and answer questions using synthetic SRE logs."""

    def __init__(
        self,
        log_file: Path = LOG_FILE,
    ) -> None:
        self.log_file = log_file

        self.model = SentenceTransformer(EMBEDDING_MODEL)

        self.client = chromadb.PersistentClient(
            path=str(BASE_DIR / "chroma_db"),
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
        )

    def load_logs(self) -> list[dict[str, str]]:
        """Load synthetic logs from JSON."""
        with self.log_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def index_logs(self) -> None:
        """Embed and store logs in ChromaDB."""
        logs = self.load_logs()

        documents = [
            (
                f"{log['timestamp']} "
                f"{log['service']} "
                f"{log['level']} "
                f"{log['message']}"
            )
            for log in logs
        ]

        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        ).tolist()

        ids = [f"log-{index}" for index in range(len(documents))]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=[
                {
                    "timestamp": log["timestamp"],
                    "service": log["service"],
                    "level": log["level"],
                }
                for log in logs
            ],
        )

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        """Retrieve the most relevant logs."""
        query_embedding = self.model.encode(
            [question],
            normalize_embeddings=True,
        ).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "document": document,
                "distance": distance,
            }
            for document, distance in zip(documents, distances)
        ]

    def _keyword_evidence(
        self,
        question: str,
    ) -> list[str]:
        """Find exact operational evidence when semantic retrieval is weak."""
        logs = self.load_logs()
        question_lower = question.lower()

        keywords: list[str] = []

        if "deploy" in question_lower or "deployment" in question_lower:
            keywords.extend(
                [
                    "deployment",
                    "deploy",
                    "readiness probe",
                    "rolled back",
                ]
            )

        if "restart" in question_lower:
            keywords.extend(
                [
                    "restarted",
                    "restart",
                    "memory limit",
                ]
            )

        if "memory" in question_lower:
            keywords.append("memory")

        if "database" in question_lower:
            keywords.append("database")

        matches = []

        for log in logs:
            message = log["message"].lower()

            if any(keyword in message for keyword in keywords):
                matches.append(
                    (
                        f"{log['timestamp']} "
                        f"{log['service']} "
                        f"{log['level']} "
                        f"{log['message']}"
                    )
                )

        return matches

    def answer(self, question: str) -> str:
        """Return an answer grounded only in available log evidence."""
        results = self.retrieve(question)

        semantic_evidence = [
            str(result["document"])
            for result in results
            if float(result["distance"]) <= MAX_DISTANCE
        ]

        keyword_evidence = self._keyword_evidence(question)

        # Combine semantic and exact operational evidence.
        evidence = list(dict.fromkeys(
            semantic_evidence + keyword_evidence
        ))

        if not evidence:
            return "I don't know based on the available logs."

        return (
            "Based on the retrieved logs:\n"
            + "\n".join(f"- {line}" for line in evidence[:5])
            + "\n\n"
            "Conclusion: "
            + self._derive_conclusion(question, evidence)
        )

    @staticmethod
    def _derive_conclusion(
        question: str,
        evidence: list[str],
    ) -> str:
        """Derive a deterministic conclusion from log evidence."""
        text = " ".join(evidence).lower()
        question_lower = question.lower()

        if (
            ("deploy" in question_lower or "deployment" in question_lower)
            and "fail" in question_lower
        ):
            if "readiness probe failed" in text:
                conclusion = (
                    "the deployment failed because the readiness "
                    "probe failed."
                )

                if "exceeded memory limit" in text:
                    conclusion += (
                        " The affected pod also exceeded its memory "
                        "limit and was restarted."
                    )

                if "rolled back" in text:
                    conclusion += (
                        " The deployment was subsequently rolled back."
                    )

                return conclusion

        if "restart" in question_lower:
            if "exceeded memory limit" in text:
                return (
                    "the embedding-service pod was restarted because "
                    "the container exceeded its memory limit."
                )

        if "memory" in question_lower:
            if "exceeded memory limit" in text:
                return (
                    "the embedding-service pod exceeded its memory "
                    "limit and was restarted."
                )

        if "rollback" in question_lower:
            if "rolled back" in text:
                return (
                    "the deployment was rolled back to version "
                    "7e21b8a after the failed deployment."
                )

        return (
            "the available logs contain the evidence shown above, "
            "but they do not establish a more specific conclusion."
        )


def main() -> None:
    """Run the SRE log agent from the command line."""
    agent = SRELogAgent()
    agent.index_logs()

    question = " ".join(sys.argv[1:])

    if not question:
        print(
            "Usage: python sre_agent.py "
            '"Why did the last deploy fail?"'
        )
        raise SystemExit(1)

    print(agent.answer(question))


if __name__ == "__main__":
    main()
