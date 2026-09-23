"""Tests for the SRE log intelligence agent."""

from pathlib import Path

from app.sre_agent import SRELogAgent


LOG_FILE = (
    Path(__file__).resolve().parent.parent
    / "logs"
    / "synthetic_logs.json"
)


def create_agent() -> SRELogAgent:
    """Create and index a test agent."""
    agent = SRELogAgent(log_file=LOG_FILE)
    agent.index_logs()
    return agent


def test_deployment_failure_is_grounded() -> None:
    """The agent should identify the deployment failure."""
    agent = create_agent()

    answer = agent.answer("Why did the last deploy fail?")

    assert "readiness probe failed" in answer


def test_memory_issue_is_grounded() -> None:
    """The agent should identify the memory failure."""
    agent = create_agent()

    answer = agent.answer("Why was the embedding pod restarted?")

    assert "memory limit" in answer


def test_unknown_question_does_not_hallucinate() -> None:
    """The agent should admit when evidence is unavailable."""
    agent = create_agent()

    answer = agent.answer(
        "What database caused the payment service outage?"
    )

    assert "I don't know" in answer
    