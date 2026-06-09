# Antigravity IDE & CLI Setup

Set up KubeShark in Google Antigravity IDE, the Antigravity CLI, or the Python SDK.

---

## Prerequisites

Before installing KubeShark for Antigravity, ensure you have:

1. **Python 3.10+** installed
2. **`google-antigravity` package** installed:
   ```bash
   pip install google-antigravity
   ```
3. **A valid Gemini API key** — required for all Antigravity agent operations

### Getting Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/api-keys)
2. Sign in with your Google account
3. Click **Create API key**
4. Copy the generated key
5. Set it as an environment variable:

   **macOS / Linux:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

   **Windows (PowerShell):**
   ```powershell
   $env:GEMINI_API_KEY = "your-api-key-here"
   ```

   **Persistent (add to shell profile):**
   ```bash
   echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

   Alternatively, create a `.env` file in your project root:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

---

## Option A: Antigravity IDE Plugin Install

Install KubeShark as a plugin so Antigravity IDE auto-discovers it for every session.

**macOS / Linux:**

```bash
git clone https://github.com/LukasNiessen/kubernetes-skill.git ~/.gemini/config/plugins/kubeshark
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/LukasNiessen/kubernetes-skill.git "$env:USERPROFILE\.gemini\config\plugins\kubeshark"
```

The IDE reads `.antigravity-plugin/plugin.json` and discovers the skill automatically. No restart needed — KubeShark activates on the next Kubernetes-related prompt.

---

## Option B: Antigravity CLI with Skill Path

Use the `--skills-path` flag to load KubeShark from any directory:

```bash
# Clone anywhere
git clone https://github.com/LukasNiessen/kubernetes-skill.git ~/skills/kubernetes-skill

# Pass to Antigravity CLI
antigravity --skills-path ~/skills/kubernetes-skill
```

This is useful when you want to keep skills outside the global plugin directory or load different skill sets per project.

---

## Option C: SDK Programmatic Usage

Load KubeShark directly in Python code using the `skills_paths` parameter:

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
)

async with Agent(config) as agent:
    response = await agent.chat(
        "Create a production-ready Deployment with security contexts "
        "and resource limits for Kubernetes 1.30"
    )
    print(await response.text())
```

The `skills_paths` parameter accepts:
- A **directory containing skill folders** (each with a `SKILL.md`) — the agent discovers all skills in that directory
- A **direct path to a specific skill folder** (containing `SKILL.md`) — loads just that skill

See the [Antigravity Usage Guide](../guides/antigravity-usage.md) for advanced SDK patterns.

---

## Verification

Confirm KubeShark is loaded by asking the agent to list its skills:

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
)

async with Agent(config) as agent:
    response = await agent.chat("List your available skills and describe them.")
    print(await response.text())
```

The agent should report the `kubernetes-skill` skill with a description mentioning Kubernetes failure modes, hallucination prevention, and manifest generation.

You can also test with a real prompt:

```
Create a Helm chart for a PostgreSQL StatefulSet with backup CronJobs
```

The response should follow the 7-step workflow and include an output contract with assumptions, failure modes, and rollback notes.

A standalone example script is available at [`examples/antigravity_agent.py`](https://github.com/LukasNiessen/kubernetes-skill/blob/main/examples/antigravity_agent.py).

---

## Updating

Pull the latest changes to update KubeShark:

**IDE plugin:**

```bash
cd ~/.gemini/config/plugins/kubeshark && git pull
```

**CLI / SDK (cloned elsewhere):**

```bash
cd /path/to/kubernetes-skill && git pull
```

---

## Uninstalling

**IDE plugin:**

```bash
rm -rf ~/.gemini/config/plugins/kubeshark
```

**CLI / SDK:**

Remove the cloned directory:

```bash
rm -rf /path/to/kubernetes-skill
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent doesn't list KubeShark as a skill | Verify `SKILL.md` exists in the path you passed to `skills_paths` |
| `GEMINI_API_KEY` errors | Ensure the key is exported: `echo $GEMINI_API_KEY` should print your key |
| `ModuleNotFoundError: google.antigravity` | Install the package: `pip install google-antigravity` |
| Skill loads but doesn't follow the workflow | Ensure you cloned the full repository, including the `references/` directory |
| Plugin not discovered by IDE | Check the path is exactly `~/.gemini/config/plugins/kubeshark/` and contains `.antigravity-plugin/plugin.json` |
