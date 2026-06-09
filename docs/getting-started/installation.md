# Installation

KubeShark can be installed in four ways depending on your environment: direct clone (recommended for Claude Code), marketplace install, per-project setup for Codex, or Antigravity IDE plugin/SDK.

---

## Option 1: Direct Clone (Recommended)

Clone the repository into your Claude Code skills directory. Claude Code auto-discovers skills in `~/.claude/skills/` -- no restart or configuration needed.

### macOS / Linux

```bash
git clone https://github.com/LukasNiessen/kubernetes-skill.git ~/.claude/skills/kubernetes-skill
```

### Windows (PowerShell)

```powershell
git clone https://github.com/LukasNiessen/kubernetes-skill.git "$env:USERPROFILE\.claude\skills\kubernetes-skill"
```

### Windows (Command Prompt)

```cmd
git clone https://github.com/LukasNiessen/kubernetes-skill.git "%USERPROFILE%\.claude\skills\kubernetes-skill"
```

After cloning, the skill is active immediately. Claude Code reads `SKILL.md` on the next Kubernetes-related prompt.

---

## Option 2: Marketplace Install

Claude Code includes a built-in plugin system with marketplace support. This avoids manual cloning.

**Add the marketplace source and install:**

```
/plugin marketplace add LukasNiessen/kubernetes-skill
/plugin install kubernetes-skill
```

**Or use the interactive manager:**

1. Run `/plugin` in Claude Code.
2. Switch to the **Discover** tab.
3. Find KubeShark and install.

The marketplace reads `.claude-plugin/marketplace.json` in the repository to register KubeShark as an installable plugin.

---

## Option 3: Codex Per-Project Setup

Codex has no global skill system. Setup is per-project: clone the skill into your repository and reference it from `AGENTS.md`.

**Step 1 -- Clone into your project:**

```bash
git clone https://github.com/LukasNiessen/kubernetes-skill.git .kubernetes-skill
```

**Step 2 -- Reference in AGENTS.md:**

Create or edit `AGENTS.md` in your repository root and add:

```markdown
## Kubernetes

When working with Kubernetes manifests, Helm charts, or Kustomize overlays,
follow the workflow in `.kubernetes-skill/SKILL.md`.
Load references from `.kubernetes-skill/references/` as needed.
```

Codex will follow the workflow whenever it encounters Kubernetes tasks in the project.

---

## Option 4: Antigravity IDE

Antigravity IDE supports KubeShark as a native plugin or via the Python SDK.

### IDE Plugin Install

Clone KubeShark into the Antigravity plugin directory:

**macOS / Linux:**

```bash
git clone https://github.com/LukasNiessen/kubernetes-skill.git ~/.gemini/config/plugins/kubeshark
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/LukasNiessen/kubernetes-skill.git "$env:USERPROFILE\.gemini\config\plugins\kubeshark"
```

The IDE reads `.antigravity-plugin/plugin.json` and discovers the skill automatically. No restart needed.

### SDK Programmatic Usage

Load KubeShark directly in Python via `skills_paths`:

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(
    skills_paths=["/path/to/kubernetes-skill"],
)

async with Agent(config) as agent:
    response = await agent.chat("Create a production Deployment for Kubernetes 1.30")
    print(await response.text())
```

**Prerequisites:** Python 3.10+, `pip install google-antigravity`, and a `GEMINI_API_KEY` environment variable. See the full [Antigravity Setup Guide](antigravity-setup.md) for API key instructions and advanced patterns.

---

## Updating

KubeShark is a plain Git repository. Pull the latest changes to update:

**macOS / Linux:**

```bash
cd ~/.claude/skills/kubernetes-skill && git pull
```

**Windows (PowerShell):**

```powershell
cd "$env:USERPROFILE\.claude\skills\kubernetes-skill"; git pull
```

**Codex projects:**

```bash
cd .kubernetes-skill && git pull
```

**Antigravity IDE plugin:**

```bash
cd ~/.gemini/config/plugins/kubeshark && git pull
```

---

## Uninstalling

Remove the cloned directory to uninstall.

**macOS / Linux:**

```bash
rm -rf ~/.claude/skills/kubernetes-skill
```

**Windows (PowerShell):**

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\kubernetes-skill"
```

**Codex projects:**

```bash
rm -rf .kubernetes-skill
```

Also remove the corresponding section from `AGENTS.md` if you added one.

**Antigravity IDE plugin:**

```bash
rm -rf ~/.gemini/config/plugins/kubeshark
```

**Marketplace installs:**

```
/plugin uninstall kubernetes-skill
```

---

## Verifying Installation

Confirm the skill is installed correctly by checking that `SKILL.md` exists:

**macOS / Linux:**

```bash
ls ~/.claude/skills/kubernetes-skill/SKILL.md
```

**Windows (PowerShell):**

```powershell
Test-Path "$env:USERPROFILE\.claude\skills\kubernetes-skill\SKILL.md"
```

If the file exists, KubeShark is ready. You can also verify by asking Claude Code a Kubernetes question -- the response should follow the 7-step workflow and include an output contract with assumptions, failure modes, and rollback notes.

**Antigravity IDE:**

```bash
ls ~/.gemini/config/plugins/kubeshark/SKILL.md
```

Or verify via the SDK by asking the agent to list its skills. See the [Antigravity Setup Guide](antigravity-setup.md) for verification details.
