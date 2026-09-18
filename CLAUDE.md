# Claude Code Configuration for ASDLC (AI-SDLC)

<!-- ASDLC-GOVERNANCE-INJECTION -->
@.agents/rules/asdlc-lifecycle-rules.md
@.agents/skills/asdlc-two-phase-governance/SKILL.md

## Commands
- `/status`: Run `asdlc status` to view current SDLC phase and guardrail status.
- `/triage $ISSUE`: Run `asdlc triage "$ISSUE"` to perform 4D Auto-triage.
- `/review $DOC`: Run `asdlc review "$DOC"` to execute The Meisters Council review (Meisters Review).
- `/advance`: Advance to next phase after clearing guardrails.
- `/code $INTENT`: Run `asdlc code "$INTENT"` to synthesize standardized code with 3-layer context.

## Guidelines
- Follow The Meisters Council Charter in `docs/charter/MEISTERS_CHARTER.md`.
- Never modify code directly without corresponding plan & human approval (`asdlc-two-phase-governance`).
- Output changes to `.devs/changes/<change-id>/plan.md` and obtain approval before applying edits.
