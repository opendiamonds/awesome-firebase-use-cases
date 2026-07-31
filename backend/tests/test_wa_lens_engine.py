"""Unit tests for offline Custom Lens riskRules scoring (A3 POC)."""

from __future__ import annotations

import unittest

from services.wa_lens_engine import (
    LENS_ID,
    heuristic_answers_from_diagram,
    list_questions,
    load_lens,
    risk_for_question,
    score_answers,
)


class TestWaLensEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.lens = load_lens()

    def test_load_lens_schema(self) -> None:
        self.assertEqual(self.lens.get("schemaVersion"), "2021-11-01")
        qs = list_questions(self.lens)
        self.assertGreaterEqual(len(qs), 5)
        self.assertEqual(LENS_ID, "cloud360-core-mvp")

    def test_risk_rules_and_or_default(self) -> None:
        qs = {q["question_id"]: q for q in list_questions(self.lens)}
        sec = qs["sec_edge"]
        self.assertEqual(
            risk_for_question(sec, ["sec_edge_waf", "sec_edge_tls"]), "NO_RISK"
        )
        self.assertEqual(risk_for_question(sec, ["sec_edge_waf"]), "MEDIUM_RISK")
        self.assertEqual(risk_for_question(sec, []), "HIGH_RISK")

    def test_score_answers_risk_counts(self) -> None:
        answers = {
            "sec_edge": ["sec_edge_waf", "sec_edge_tls"],
            "sec_data": [],
            "rel_ha": ["rel_ha_multiaz"],
            "cost_storage": [],
            "perf_cache": ["perf_cache_present"],
            "oe_observe": [],
        }
        # Only include ids present in lens
        valid = {q["question_id"] for q in list_questions(self.lens)}
        answers = {k: v for k, v in answers.items() if k in valid}
        out = score_answers(self.lens, answers)
        self.assertIn("risk_counts", out)
        rc = out["risk_counts"]
        self.assertEqual(rc["NO_RISK"] + rc["MEDIUM_RISK"] + rc["HIGH_RISK"], len(answers))
        self.assertGreaterEqual(out["overall_score"], 0)
        self.assertLessEqual(out["overall_score"], 100)
        self.assertIn("security", out["pillar_scores"])

    def test_heuristic_answers_from_diagram(self) -> None:
        xml = """
        <mxGraphModel><root>
          <mxCell id="1" value="AWS WAF" style=""/>
          <mxCell id="2" value="HTTPS / TLS ACM" style=""/>
          <mxCell id="3" value="ElastiCache Redis" style=""/>
          <mxCell id="4" value="Multi-AZ RDS" style=""/>
        </root></mxGraphModel>
        """
        answers = heuristic_answers_from_diagram(xml, self.lens)
        self.assertIn("sec_edge_waf", answers.get("sec_edge", []))
        self.assertIn("sec_edge_tls", answers.get("sec_edge", []))
        self.assertIn("perf_cache_present", answers.get("perf_cache", []))

    def test_findings_from_lens_high_medium_only(self) -> None:
        from services.wa_lens_engine import findings_from_lens_score

        answers = {
            "sec_edge": [],  # HIGH
            "sec_data": ["sec_data_encrypt"],  # MEDIUM
            "rel_ha": ["rel_ha_multiaz", "rel_ha_standby"],  # NO
            "cost_storage": ["cost_lifecycle"],  # NO
            "perf_cache": [],  # MEDIUM
            "oe_observe": ["oe_monitor", "oe_alarm"],  # NO
        }
        valid = {q["question_id"] for q in list_questions(self.lens)}
        answers = {k: v for k, v in answers.items() if k in valid}
        scored = score_answers(self.lens, answers)
        findings = findings_from_lens_score(self.lens, scored)
        risks = {f["lens_risk"] for f in findings}
        self.assertNotIn("NO_RISK", risks)
        self.assertTrue(risks <= {"HIGH_RISK", "MEDIUM_RISK"})
        self.assertTrue(all(f["source"] == "offline_lens" for f in findings))
        sev = {f["severity"] for f in findings}
        self.assertTrue(sev <= {"high", "warn"})
        # empty answers for sec_edge → HIGH → high
        sec = next(f for f in findings if f["question_id"] == "sec_edge")
        self.assertEqual(sec["severity"], "high")
        self.assertTrue(sec["recommendation_hint"])


if __name__ == "__main__":
    unittest.main()
