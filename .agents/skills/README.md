# Moved → `.kiro/skills/`

The Cetana Labs skill suite has migrated to the **Kiro-native** location:

> **`.kiro/skills/<name>/SKILL.md`**

This makes each skill a real invokable `/command` shared automatically across **Kiro Web** and **Kiro IDE** (committed to the repo). See [AGENTS.md §4](../../AGENTS.md) for the full command list and `.kiro/steering/` for conventions.

Personal commands (`/sign-in`, `/sign-off`, `/session-save`, `/session-resume`) live in the developer's local `~/.kiro/skills/` and sync to Web via Configuration Sync.

_This directory is retained only as a redirect; do not add new skills here._
