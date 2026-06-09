# Antigravity SDK Integration

Advanced patterns for integrating KubeShark with the Google Antigravity SDK to build specialized Kubernetes agents.

---

## Building a Kubernetes Agent

At its simplest, a Kubernetes agent loads KubeShark as a skill and answers Kubernetes questions using the failure-mode workflow:

```python
import asyncio
from google.antigravity import Agent, LocalAgentConfig

async def main():
    config = LocalAgentConfig(
        skills_paths=["/path/to/kubernetes-skill"],
    )

    async with Agent(config) as agent:
        response = await agent.chat("Create an HPA for my Deployment targeting 70% CPU")
        print(await response.text())

asyncio.run(main())
```

The sections below show how to build more sophisticated agents by combining KubeShark with other SDK capabilities.

---

## Combining with MCP Servers

MCP (Model Context Protocol) servers extend your agent with live data. For Kubernetes work, the most valuable MCP integrations are:

### kubectl as an MCP Tool

Connect a kubectl MCP server so the agent can query live cluster state during diagnosis:

```python
from google.antigravity import Agent, LocalAgentConfig, types

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    mcp_servers=[
        types.McpStdioServer(
            command="npx",
            args=["-y", "@kubernetes/mcp-server"],
        ),
    ],
)

async with Agent(config) as agent:
    response = await agent.chat(
        "Check the current cluster version and available API groups, "
        "then create a Deployment that uses the correct apiVersions "
        "for this specific cluster."
    )
    print(await response.text())
```

### Custom Cluster Info Provider

Build a Python MCP server that provides organization-specific context:

```python
config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    mcp_servers=[
        types.McpStdioServer(
            command="python3",
            args=["cluster_info_mcp.py"],
        ),
    ],
)
```

Your MCP server (`cluster_info_mcp.py`) could expose tools like:
- `get_cluster_version()` — returns the Kubernetes version
- `get_namespace_policies(ns)` — returns PSA level, quotas, required labels
- `get_approved_registries()` — returns allowed image registries
- `get_installed_crds()` — returns CRDs for CRR signal detection

See the [MCP Integration guide](mcp-integration.md) for safe integration patterns and output hygiene rules.

---

## Safety Policies for Kubernetes Operations

When allowing the agent to run kubectl commands, use safety policies to limit what it can do:

```python
from google.antigravity import Agent, LocalAgentConfig, policy

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    safety_policies=[
        # Deny everything by default
        policy.deny_all(),

        # Allow read-only kubectl commands
        policy.allow("run_command", predicate=lambda cmd: (
            cmd.startswith("kubectl get") or
            cmd.startswith("kubectl describe") or
            cmd.startswith("kubectl logs") or
            cmd.startswith("kubectl diff") or
            cmd.startswith("kubectl api-versions") or
            cmd.startswith("kubectl api-resources") or
            cmd.startswith("kubeconform")
        )),

        # Allow dry-run applies (validation only)
        policy.allow("run_command", predicate=lambda cmd: (
            "kubectl apply" in cmd and "--dry-run=server" in cmd
        )),

        # Allow all file operations for manifest generation
        policy.allow("view_file"),
        policy.allow("create_file"),
        policy.allow("edit_file"),
        policy.allow("list_directory"),
    ],
)
```

This lets the agent:
- Read cluster state for accurate diagnosis (Step 1)
- Run dry-run validation (Step 6)
- Generate and edit manifest files (Step 5)

But prevents:
- Direct applies to the cluster (`kubectl apply` without `--dry-run`)
- Destructive operations (`kubectl delete`, `kubectl drain`)
- Arbitrary command execution

---

## Hooks for Manifest Audit

Use lifecycle hooks to intercept agent actions and add custom validation:

```python
from google.antigravity import Agent, LocalAgentConfig

async def pre_tool_hook(tool_name, tool_args, context):
    """Audit all file creation to ensure manifests meet org policies."""
    if tool_name == "create_file" and tool_args.get("path", "").endswith((".yaml", ".yml")):
        content = tool_args.get("content", "")

        # Check for organization-required labels
        if "team:" not in content and "cost-center:" not in content:
            print(f"AUDIT WARNING: Manifest missing required org labels: {tool_args['path']}")

        # Check for image registry compliance
        if "docker.io/" in content or ":latest" in content:
            print(f"AUDIT WARNING: Non-compliant image reference in: {tool_args['path']}")

    return tool_args  # Return unchanged (or modify to inject labels)


async def post_turn_hook(turn_result, context):
    """Log output contract details for compliance tracking."""
    text = turn_result.text if hasattr(turn_result, 'text') else str(turn_result)
    if "assumptions" in text.lower() and "rollback" in text.lower():
        print("AUDIT: Output contract detected — logging for compliance")


config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    hooks={
        "pre_tool": pre_tool_hook,
        "post_turn": post_turn_hook,
    },
)
```

---

## Structured Output for CI Integration

Parse KubeShark output into typed Python objects for CI pipeline integration:

```python
from pydantic import BaseModel, Field
from google.antigravity import Agent, LocalAgentConfig


class ManifestReview(BaseModel):
    """Structured output from a KubeShark security review."""

    cluster_version_floor: str = Field(
        description="Minimum Kubernetes version assumed"
    )
    failure_modes_detected: list[str] = Field(
        description="Failure modes diagnosed by the workflow"
    )
    severity: str = Field(
        description="Overall severity: critical, high, medium, low"
    )
    issues: list[str] = Field(
        description="Specific issues found in the manifest"
    )
    remediated_manifest: str = Field(
        description="The fixed YAML manifest"
    )
    validation_commands: list[str] = Field(
        description="Commands to validate the remediated manifest"
    )
    rollback_command: str = Field(
        description="Command to rollback if the fix causes issues"
    )


async def ci_review(manifest_path: str) -> ManifestReview:
    """Run a KubeShark review as part of a CI pipeline."""
    config = LocalAgentConfig(
        skills_paths=["/path/to/kubernetes-skill"],
    )

    manifest_content = open(manifest_path).read()

    async with Agent(config) as agent:
        response = await agent.chat(
            f"Review this Kubernetes manifest for all failure modes. "
            f"Return structured output.\n\n{manifest_content}",
            output_schema=ManifestReview,
        )
        return await response.parsed()


# Usage in CI:
# result = asyncio.run(ci_review("k8s/deployment.yaml"))
# if result.severity in ("critical", "high"):
#     sys.exit(1)  # Fail the pipeline
```

---

## Subagent Patterns

Use subagents to separate diagnosis from generation for complex Kubernetes work:

```python
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.types import TemplatedSystemInstructions

# Diagnosis agent — reads manifests, identifies failure modes
diagnosis_config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    system_instructions=TemplatedSystemInstructions(
        identity=(
            "You are a Kubernetes diagnosis specialist. "
            "Your job is to identify failure modes in Kubernetes manifests "
            "following the KubeShark workflow Steps 1-2. "
            "Do NOT generate fixes — only diagnose."
        ),
    ),
)

# Remediation agent — generates fixed manifests
remediation_config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    system_instructions=TemplatedSystemInstructions(
        identity=(
            "You are a Kubernetes remediation specialist. "
            "Given a diagnosis of failure modes, generate production-ready "
            "fixed manifests following KubeShark workflow Steps 3-7."
        ),
    ),
)


async def diagnose_and_fix(manifest: str):
    """Two-phase workflow: diagnose then remediate."""

    # Phase 1: Diagnosis
    async with Agent(diagnosis_config) as diagnoser:
        diagnosis = await diagnoser.chat(
            f"Diagnose all failure modes in this manifest:\n\n{manifest}"
        )
        diagnosis_text = await diagnosis.text()
        print("=== DIAGNOSIS ===")
        print(diagnosis_text)

    # Phase 2: Remediation (with diagnosis context)
    async with Agent(remediation_config) as remediator:
        fix = await remediator.chat(
            f"Based on this diagnosis, generate remediated manifests:\n\n"
            f"DIAGNOSIS:\n{diagnosis_text}\n\n"
            f"ORIGINAL MANIFEST:\n{manifest}"
        )
        print("\n=== REMEDIATION ===")
        print(await fix.text())
```

---

## Persistent Kubernetes Agent

Create an agent that remembers previous interactions across sessions:

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    app_data_dir="/absolute/path/to/k8s-agent-data",
    persistence=True,
)

async with Agent(config) as agent:
    # Session 1: Set up cluster context
    await agent.chat("I'm working on a GKE Autopilot cluster running 1.30")

    # Session 2 (later): The agent remembers the cluster context
    response = await agent.chat("Create a Deployment for my API")
    # Agent knows to use GKE patterns and Autopilot constraints
    print(await response.text())
```

---

## Periodic Cluster Audit

Set up a scheduled agent that audits your manifests on a recurring basis:

```python
from google.antigravity import Agent, LocalAgentConfig, triggers
from pathlib import Path

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
    triggers=[
        triggers.FileSystemTrigger(
            paths=["/path/to/k8s-manifests/"],
            patterns=["*.yaml", "*.yml"],
            on_change="Review this changed Kubernetes manifest for all failure modes.",
        ),
    ],
)

# The agent watches for manifest file changes and auto-reviews them
async with Agent(config) as agent:
    await agent.run_forever()
```
