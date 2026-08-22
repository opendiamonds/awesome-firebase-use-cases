"""TestClient coverage for /api/cost (B1)."""

import os
import unittest

os.environ.setdefault("COST_PRICING_STUB", "1")

from fastapi.testclient import TestClient

from database import get_db
from main import app
from models import UserDiagram
from services.auth import get_current_user
from tests.helpers import close_session, make_diagram, make_session, make_user


class TestCostApiAuth(unittest.TestCase):
    def setUp(self):
        self.db = make_session()
        self.finops = make_user(self.db, username="david", role="FinOps_Analyst")
        self.architect = make_user(self.db, username="alex", role="Project_Architect")
        self.dev = make_user(self.db, username="ian", role="Developer")
        self.diagram = make_diagram(
            self.db,
            owner=self.finops,
            title="Cost test",
            xml_data=(
                '<mxGraphModel><root>'
                '<mxCell id="0"/><mxCell id="1" parent="0"/>'
                '<mxCell id="2" value="EC2" style="aws4" vertex="1" parent="1"/>'
                "</root></mxGraphModel>"
            ),
        )
        self.arch_diagram = make_diagram(
            self.db,
            owner=self.architect,
            title="Cost arch test",
            xml_data=(
                '<mxGraphModel><root>'
                '<mxCell id="0"/><mxCell id="1" parent="0"/>'
                '<mxCell id="2" value="EC2" style="aws4" vertex="1" parent="1"/>'
                "</root></mxGraphModel>"
            ),
        )
        self.db.commit()

    def tearDown(self):
        close_session(self.db)
        app.dependency_overrides.clear()

    def _client_as(self, user):
        def override_db():
            yield self.db

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = lambda: user
        return TestClient(app)

    def test_finops_can_list_diagrams(self):
        client = self._client_as(self.finops)
        resp = client.get("/api/cost/diagrams")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("items", resp.json())

    def test_developer_denied_list(self):
        client = self._client_as(self.dev)
        resp = client.get("/api/cost/diagrams")
        self.assertEqual(resp.status_code, 403)

    def test_finops_get_snapshot(self):
        client = self._client_as(self.finops)
        resp = client.get(f"/api/cost/diagrams/{self.diagram.id}")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("lines", body)
        self.assertIsNone(body.get("budget"))
        self.assertEqual(body.get("diagram_cloud"), "aws")
        self.assertEqual(
            body.get("allowed_regions"),
            [
                "us-east-1",
                "us-west-2",
                "eu-west-1",
                "ap-northeast-1",
                "ap-southeast-1",
                "ap-east-2",
            ],
        )

    def test_region_rejects_other_cloud(self):
        client = self._client_as(self.architect)
        resp = client.put(
            f"/api/cost/diagrams/{self.arch_diagram.id}/region",
            json={"region": "us-central1"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_hours_422(self):
        client = self._client_as(self.finops)
        snap = client.get(f"/api/cost/diagrams/{self.diagram.id}").json()
        mx = snap["lines"][0]["mxcell_id"]
        resp = client.put(
            f"/api/cost/diagrams/{self.diagram.id}/lines/{mx}/hours",
            json={"hours": 25},
        )
        self.assertEqual(resp.status_code, 422)

    def test_budget_route_not_registered(self):
        client = self._client_as(self.finops)
        resp = client.put(
            f"/api/cost/diagrams/{self.diagram.id}/budget",
            json={"budget": 100},
        )
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
