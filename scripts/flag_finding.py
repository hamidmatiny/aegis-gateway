#!/usr/bin/env python3
"""Deterministic helpers for /flag-finding.

The 2026-10-09T13:00Z run timed out after 3600s in the escalate step: the
agent waited on a synchronous manager chat with no budget. This script does
the packaging and the findings.md bookkeeping so the LLM only makes ONE
bounded delivery call, and records an honest status if that call stalls.

Usage:
  python3 scripts/flag_finding.py build --title T --file gateway/x.go --evidence E [--pr URL]
  python3 scripts/flag_finding.py record --title T --status delivered|timeout|failed [--ref ID]
"""
import argparse
import datetime as _dt
import re
import sys

COMPONENT = "gateway"
MANAGER = "aegis-product-eng"
MAX_MESSAGE_CHARS = 3000
# Seconds the delivery call may block before we stop waiting and record "timeout".
DELIVERY_TIMEOUT_SECONDS = 300
STATUSES = ("delivered", "timeout", "failed")

_APPROVAL = re.compile(
    r"\b(approved|authori[sz]ed|signed off|cleared|pr is (pending|open|merged))\b",
    re.IGNORECASE,
)
_PR_URL = re.compile(r"https://github\.com/hamidmatiny/[\w.-]+/pull/\d+")


def uncited_approvals(text):
    """Return sentences that use an approval word without citing a PR URL."""
    bad = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
        if _APPROVAL.search(sentence) and not _PR_URL.search(sentence):
            bad.append(sentence.strip())
    return bad


def build_message(title, files, evidence, recommended_pr=None):
    """Package a finding for the manager. Raises ValueError on bad input."""
    if not title or not title.strip():
        raise ValueError("title is required")
    if not files:
        raise ValueError("at least one file path is required")
    if not evidence or not evidence.strip():
        raise ValueError("evidence is required")
    if recommended_pr and not _PR_URL.fullmatch(recommended_pr):
        raise ValueError("recommended PR must be a hamidmatiny PR URL")

    lines = [
        f"[{COMPONENT}] finding: {title.strip()}",
        "Files: " + ", ".join(files),
        "Evidence: " + evidence.strip(),
        "Recommended PR: " + (recommended_pr or "none opened"),
        "Ask: reply with a short ACK (received / will triage). "
        "Please do not do the triage inside this reply.",
    ]
    msg = "\n".join(lines)
    if len(msg) > MAX_MESSAGE_CHARS:
        msg = msg[: MAX_MESSAGE_CHARS - 15].rstrip() + "\n[truncated]"
    bad = uncited_approvals(msg)
    if bad:
        raise ValueError("uncited approval wording: " + " | ".join(bad))
    return msg


def findings_entry(title, status, ref=None, now=None):
    """One append-only line for memory/findings.md."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    if status == "delivered" and not ref:
        raise ValueError("delivered requires a delivery ref (execution/message id)")
    now = now or _dt.datetime.now(_dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%MZ")
    if status == "delivered":
        tail = f"escalated to {MANAGER}, delivery confirmed (ref {ref})"
    elif status == "timeout":
        tail = (f"NOT escalated: delivery to {MANAGER} did not confirm within "
                f"{DELIVERY_TIMEOUT_SECONDS}s" + (f" (ref {ref})" if ref else ""))
    else:
        tail = f"NOT escalated: delivery to {MANAGER} failed" + (f" ({ref})" if ref else "")
    return f"- {stamp} — {title.strip()} — {tail}"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--title", required=True)
    b.add_argument("--file", action="append", default=[])
    b.add_argument("--evidence", required=True)
    b.add_argument("--pr")
    r = sub.add_parser("record")
    r.add_argument("--title", required=True)
    r.add_argument("--status", required=True, choices=STATUSES)
    r.add_argument("--ref")
    r.add_argument("--findings", default="memory/findings.md")
    args = p.parse_args(argv)
    try:
        if args.cmd == "build":
            print(build_message(args.title, args.file, args.evidence, args.pr))
        else:
            line = findings_entry(args.title, args.status, args.ref)
            with open(args.findings, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
            print(line)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
