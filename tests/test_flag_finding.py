import datetime as dt
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import flag_finding as ff  # noqa: E402

NOW = dt.datetime(2026, 10, 10, 3, 0, tzinfo=dt.timezone.utc)


class BuildMessageTest(unittest.TestCase):
    def test_packages_finding_and_asks_for_ack_only(self):
        msg = ff.build_message("missing failure-path tests", ["gateway/pipeline.go"],
                               "only 3 *_test.go files")
        self.assertIn("[gateway] finding: missing failure-path tests", msg)
        self.assertIn("gateway/pipeline.go", msg)
        self.assertIn("Recommended PR: none opened", msg)
        self.assertIn("ACK", msg)

    def test_rejects_missing_evidence_or_files(self):
        with self.assertRaises(ValueError):
            ff.build_message("t", [], "e")
        with self.assertRaises(ValueError):
            ff.build_message("t", ["gateway/a.go"], "  ")

    def test_rejects_uncited_approval(self):
        with self.assertRaises(ValueError):
            ff.build_message("t", ["gateway/a.go"], "Fix was approved by Hamid.")

    def test_allows_cited_approval_and_pr(self):
        url = "https://github.com/hamidmatiny/aegis/pull/12"
        msg = ff.build_message("t", ["gateway/a.go"], f"Fix approved in {url}.", url)
        self.assertIn(url, msg)

    def test_truncates_long_evidence(self):
        msg = ff.build_message("t", ["gateway/a.go"], "x" * 10000)
        self.assertLessEqual(len(msg), ff.MAX_MESSAGE_CHARS)
        self.assertTrue(msg.endswith("[truncated]"))


class RecordTest(unittest.TestCase):
    def test_delivered_requires_ref(self):
        with self.assertRaises(ValueError):
            ff.findings_entry("t", "delivered", now=NOW)

    def test_timeout_is_recorded_as_not_escalated(self):
        line = ff.findings_entry("t", "timeout", now=NOW)
        self.assertTrue(line.startswith("- 2026-10-10T03:00Z — t — NOT escalated"))
        self.assertIn(str(ff.DELIVERY_TIMEOUT_SECONDS), line)
        self.assertLessEqual(ff.DELIVERY_TIMEOUT_SECONDS, 600)

    def test_cli_record_appends(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "findings.md")
            rc = ff.main(["record", "--title", "t", "--status", "delivered",
                          "--ref", "exec-1", "--findings", path])
            self.assertEqual(rc, 0)
            with open(path, encoding="utf-8") as fh:
                self.assertIn("delivery confirmed (ref exec-1)", fh.read())

    def test_staged_skill_uses_script_and_budget(self):
        for rel in ("skill-staging/flag-finding/SKILL.md",
                    ".claude/skills/flag-finding/SKILL.md"):
            path = os.path.join(ROOT, rel)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                if "scripts/flag_finding.py" in text:
                    self.assertIn("300", text)
                    return
        self.fail("flag-finding skill does not call scripts/flag_finding.py")


if __name__ == "__main__":
    unittest.main()
