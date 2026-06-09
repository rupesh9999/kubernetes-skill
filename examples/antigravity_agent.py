#!/usr/bin/env python3
"""
KubeShark + Google Antigravity SDK — Example Agent

Demonstrates how to load the KubeShark Kubernetes skill into an Antigravity
agent for production-grade Kubernetes manifest generation.

Prerequisites:
    pip install google-antigravity
    export GEMINI_API_KEY="your-api-key"

Usage:
    python examples/antigravity_agent.py
"""

import asyncio
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve the KubeShark skill directory (parent of this script's directory)
# ---------------------------------------------------------------------------
SKILL_DIR = str(Path(__file__).resolve().parent.parent)


async def basic_usage():
    """Load KubeShark and ask a Kubernetes question."""
    from google.antigravity import Agent, LocalAgentConfig

    config = LocalAgentConfig(
        skills_paths=[SKILL_DIR],
    )

    async with Agent(config) as agent:
        # The agent automatically discovers SKILL.md and follows its workflow
        response = await agent.chat(
            "Create a production-ready Deployment for a Python Flask API "
            "with 3 replicas, resource limits, security contexts, "
            "a readiness probe, and an Ingress on Kubernetes 1.30."
        )
        print(await response.text())


async def sre_persona():
    """Load KubeShark with an SRE persona for security-focused reviews."""
    from google.antigravity import Agent, LocalAgentConfig
    from google.antigravity.types import TemplatedSystemInstructions

    config = LocalAgentConfig(
        skills_paths=[SKILL_DIR],
        system_instructions=TemplatedSystemInstructions(
            identity=(
                "You are a Senior Site Reliability Engineer specializing in "
                "Kubernetes security and production hardening. You follow the "
                "KubeShark failure-mode workflow rigorously and always produce "
                "output contracts with assumptions, tradeoffs, and rollback notes."
            ),
        ),
    )

    async with Agent(config) as agent:
        response = await agent.chat(
            "Review this Deployment for security issues:\n\n"
            "apiVersion: apps/v1\n"
            "kind: Deployment\n"
            "metadata:\n"
            "  name: web-app\n"
            "spec:\n"
            "  replicas: 2\n"
            "  selector:\n"
            "    matchLabels:\n"
            "      app: web-app\n"
            "  template:\n"
            "    metadata:\n"
            "      labels:\n"
            "        app: web-app\n"
            "    spec:\n"
            "      containers:\n"
            "      - name: web\n"
            "        image: myapp:latest\n"
            "        ports:\n"
            "        - containerPort: 8080\n"
        )
        print(await response.text())


async def list_skills():
    """Verify KubeShark is discovered by the agent."""
    from google.antigravity import Agent, LocalAgentConfig

    config = LocalAgentConfig(
        skills_paths=[SKILL_DIR],
    )

    async with Agent(config) as agent:
        response = await agent.chat(
            "List all your available skills. "
            "For each skill, show its name and a brief description."
        )
        print(await response.text())


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
EXAMPLES = {
    "basic": ("Generate a production Deployment", basic_usage),
    "sre": ("Security review with SRE persona", sre_persona),
    "list": ("List discovered skills", list_skills),
}


def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print(
            "ERROR: GEMINI_API_KEY environment variable is not set.\n"
            "Get a key at: https://aistudio.google.com/app/api-keys\n"
            "Then run:  export GEMINI_API_KEY='your-key-here'"
        )
        sys.exit(1)

    choice = sys.argv[1] if len(sys.argv) > 1 else "basic"

    if choice not in EXAMPLES:
        print(f"Usage: python {sys.argv[0]} [{' | '.join(EXAMPLES)}]")
        print()
        for key, (desc, _) in EXAMPLES.items():
            print(f"  {key:8s}  {desc}")
        sys.exit(1)

    desc, func = EXAMPLES[choice]
    print(f"Running: {desc}\n{'=' * 60}\n")
    asyncio.run(func())


if __name__ == "__main__":
    main()
