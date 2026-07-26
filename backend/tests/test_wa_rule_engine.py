"""Property-based + unit tests for WaRuleEngine (A3)."""

from __future__ import annotations

import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

import tests.helpers  # noqa: F401 — path / psycopg2 setup
from services.wa_rule_engine import (
    WEIGHTS,
    evaluate,
    score_findings,
    Finding,
    PILLARS,
)


def _mx(cells: list[str]) -> str:
    inner = "".join(cells)
    return f"<mxGraphModel><root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/>{inner}</root></mxGraphModel>"


class TestWaRuleEngine(unittest.TestCase):
    def test_empty_diagram_has_finding(self):
        result = evaluate(_mx([]))
        codes = {f.code for f in result.findings}
        self.assertIn("OE-EMPTY-DIAGRAM", codes)
        self.assertEqual(result.rule_pack_version, "wa-aws-mvp-1")

    def test_db_without_standby(self):
        xml = _mx(
            [
                '<mxCell id="10" value="Aurora PostgreSQL" style="shape=mxgraph.aws4.rds;" vertex="1" parent="1"/>',
            ]
        )
        result = evaluate(xml)
        codes = {f.code for f in result.findings}
        self.assertIn("REL-DB-NO-STANDBY", codes)

    @given(
        severities=st.lists(
            st.sampled_from(["info", "warn", "high", "critical"]),
            min_size=0,
            max_size=8,
        )
    )
    @settings(max_examples=40)
    def test_scores_bounded_and_weighted(self, severities):
        findings = [
            Finding(
                code=f"T-{i}",
                pillar=PILLARS[i % len(PILLARS)],
                severity=sev,
                title="t",
                message="m",
            )
            for i, sev in enumerate(severities)
        ]
        pillar_scores, overall = score_findings(findings)
        for p in PILLARS:
            self.assertGreaterEqual(pillar_scores[p], 0.0)
            self.assertLessEqual(pillar_scores[p], 100.0)
        expected = sum(pillar_scores[p] * WEIGHTS[p] for p in PILLARS)
        self.assertAlmostEqual(overall, round(expected, 2), places=2)

    @given(n=st.integers(min_value=0, max_value=5))
    @settings(max_examples=20)
    def test_same_xml_deterministic(self, n):
        cells = [
            f'<mxCell id="{i+10}" value="EC2 app {i}" style="shape=mxgraph.aws4.ec2;" vertex="1" parent="1"/>'
            for i in range(n)
        ]
        xml = _mx(cells)
        a = evaluate(xml)
        b = evaluate(xml)
        self.assertEqual(
            [f.code for f in a.findings],
            [f.code for f in b.findings],
        )
        self.assertEqual(a.overall_score, b.overall_score)
        self.assertEqual(a.pillar_scores, b.pillar_scores)

    def test_deduction_lowers_score(self):
        findings = [
            Finding(
                code="X",
                pillar="security",
                severity="critical",
                title="t",
                message="m",
            )
        ]
        pillar_scores, _ = score_findings(findings)
        self.assertEqual(pillar_scores["security"], 75.0)


if __name__ == "__main__":
    unittest.main()
