---
name: flag-finding
description: Escalate a real gateway finding to aegis-product-eng with confirmed delivery
user-invocable: true
---

# Flag Finding

**Time budget:** the whole skill must finish in under 10 minutes. On 2026-10-09 an
escalation ran into the 3600s task timeout because it blocked on a synchronous
manager chat. Never wait on the manager to finish *their* work — you only need an ACK.

1. Package (deterministic — do not hand-write it):
   `python3 scripts/flag_finding.py build --title "<title>" --file gateway/<path> [--file ...] --evidence "<evidence>" [--pr <PR URL>]`
   - Exit code 2 = bad input or uncited approval wording; fix the input, do not bypass.
2. Deliver **once**: `mcp__trinity__chat_with_agent` → `aegis-product-eng` with the
   script output as the message. Use async/fire-and-forget mode or a timeout ≤ 300s if
   the tool offers it. Do **not** retry in a loop, and do not chain further agent calls.
3. Record the real outcome (exactly one):
   - confirmed ACK/execution id → `python3 scripts/flag_finding.py record --title "<title>" --status delivered --ref <id>`
   - no confirmation within 300s → `... record --title "<title>" --status timeout [--ref <id>]`
   - tool error → `... record --title "<title>" --status failed --ref "<error>"`
4. On `timeout`/`failed`: operator-queue alert + honest Slack close-out stating the
   finding is **not** escalated. Claim "escalated" only for `delivered`.
