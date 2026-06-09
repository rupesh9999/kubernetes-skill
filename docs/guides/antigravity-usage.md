# Antigravity Usage Guide

How to use KubeShark with the Google Antigravity SDK, IDE, and CLI for Kubernetes manifest generation, security reviews, and infrastructure hardening.

---

## How Skills Work in Antigravity

Antigravity agents load skills from the filesystem. A skill is a directory containing a `SKILL.md` file with YAML frontmatter that defines the skill's name and description, plus optional reference files, scripts, and assets.

When KubeShark is loaded, the agent gains:

- The **7-step failure-mode workflow** defined in `SKILL.md`
- Access to **26 reference files** covering security, networking, RBAC, probes, Helm, Kustomize, and more
- **Conditional Reference Retrieval (CRR)** for EKS, GKE, AKS, OpenShift, GitOps, and observability stacks

The agent reads `SKILL.md` and follows its diagnostic workflow whenever it encounters a Kubernetes task — the same behavior as Claude Code and Codex.

---

## Natural Language Usage

Once loaded, KubeShark activates automatically for Kubernetes-related prompts. No special syntax needed:

```
Create a production-ready Deployment for a Node.js API with autoscaling
```

```
Review my StatefulSet for security and reliability issues
```

```
Build a Kustomize overlay structure with base, staging, and production variants
```

Every response follows the 7-step workflow and includes an output contract with assumptions, tradeoffs, and rollback notes.

---

## SDK Patterns

### Basic: Load and Query

```python
import asyncio
from google.antigravity import Agent, LocalAgentConfig

async def main():
    config = LocalAgentConfig(
        skills_paths=["/path/to/kubernetes-skill"],
    )

    async with Agent(config) as agent:
        response = await agent.chat(
            "Create a production Deployment for a Python Flask API "
            "with 3 replicas, resource limits, and an Ingress "
            "on Kubernetes 1.30."
        )
        print(await response.text())

asyncio.run(main())
```

### SRE Persona for Security Reviews

Combine KubeShark with a custom persona to get security-focused output:

```python
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.types import TemplatedSystemInstructions

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
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
        "Review this manifest for security issues:\n\n"
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
```

### Multi-Skill Loading

Load KubeShark alongside other skills for broader agent capabilities:

```python
config = LocalAgentConfig(
    skills_paths=[
        "/path/to/kubernetes-skill",      # KubeShark
        "/path/to/other-skills-directory", # Other skills (agent discovers all)
    ],
)
```

Each path can be:
- A **direct skill folder** (containing `SKILL.md`) — loads that specific skill
- A **parent directory** of skill folders — discovers all skills within it

### Streaming Responses

For long manifest generation tasks, stream the response to see output in real-time:

```python
async with Agent(config) as agent:
    response = await agent.chat(
        "Create a complete Helm chart for a Redis cluster "
        "with configurable replicas and persistent storage"
    )

    async for chunk in response.stream():
        print(chunk.text, end="", flush=True)
```

### Structured Output for CI Pipelines

Use structured output to parse KubeShark responses programmatically:

```python
from pydantic import BaseModel
from google.antigravity import Agent, LocalAgentConfig

class KubeSharkOutput(BaseModel):
    assumptions: list[str]
    failure_modes: list[str]
    manifests: str
    validation_commands: list[str]
    rollback_notes: str

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
)

async with Agent(config) as agent:
    response = await agent.chat(
        "Create a NetworkPolicy that allows only frontend pods "
        "to reach the backend on port 8080. "
        "Return structured output.",
        output_schema=KubeSharkOutput,
    )
    result = await response.parsed()
    # result.manifests contains the YAML
    # result.validation_commands contains kubectl commands to verify
```

---

## IDE Workflow

When KubeShark is installed as an Antigravity IDE plugin (in `~/.gemini/config/plugins/kubeshark/`), it integrates directly into your coding workflow:

1. **Open any Kubernetes manifest** (`.yaml`, `.yml`) or Helm chart in the IDE
2. **Ask a question** in the chat panel — KubeShark activates automatically for Kubernetes tasks
3. **Review the structured output** — the agent follows the 7-step workflow with failure mode diagnosis
4. **Apply suggestions** — use the IDE's inline diff to review and apply manifest changes

### Example IDE Prompts

| Task | Prompt |
|------|--------|
| Security review | "Review this Deployment for security issues and add proper RBAC" |
| Manifest creation | "Create a StatefulSet for PostgreSQL with persistent storage" |
| Helm chart | "Generate a Helm chart for this application with staging and production values" |
| Troubleshooting | "My pods are stuck in CrashLoopBackOff with OOMKilled — diagnose this manifest" |
| Policy check | "Add Kyverno policies to enforce resource limits across the namespace" |
| Platform-specific | "Adapt this Deployment for EKS with IRSA and AWS Load Balancer Controller" |

---

## Differences from Claude Code and Codex

| Dimension | Claude Code | Codex | Antigravity |
|-----------|-------------|-------|-------------|
| **Skill discovery** | `~/.claude/skills/` auto-scan | Per-project via `AGENTS.md` | `skills_paths` in config or `~/.gemini/config/plugins/` |
| **Invocation** | `/kubernetes-skill` or natural | Natural (via AGENTS.md) | Natural (via skill loading) |
| **Plugin system** | `.claude-plugin/marketplace.json` | None | `.antigravity-plugin/plugin.json` |
| **Programmatic use** | No SDK | No SDK | `google.antigravity` Python SDK |
| **Custom persona** | Via system prompt | Via AGENTS.md | `TemplatedSystemInstructions` |
| **Structured output** | Not available | Not available | Pydantic models via `output_schema` |
| **MCP integration** | Native | Not available | `McpStdioServer` / `McpSseServer` |
| **Subagents** | Not available | Not available | `start_subagent` tool |

The core KubeShark behavior — the 7-step workflow, failure mode diagnosis, reference loading, and output contracts — is identical across all three platforms. The differences are in how the skill is loaded and what additional SDK features are available.
