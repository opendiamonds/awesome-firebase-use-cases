"""Unit tests for diagram_builder geometry + XML assembly (A1)."""

from __future__ import annotations

import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from hypothesis import given, settings, strategies as st

from tests.helpers import backend_dir  # noqa: F401

from services.diagram_builder import build_mxgraph_xml, is_inside


class TestIsInside(unittest.TestCase):
    def test_fully_inside(self):
        parent = {"x": 0, "y": 0, "width": 400, "height": 300}
        child = {"x": 10, "y": 10, "width": 80, "height": 80}
        self.assertTrue(is_inside(child, parent))

    def test_outside(self):
        parent = {"x": 0, "y": 0, "width": 100, "height": 100}
        child = {"x": 50, "y": 50, "width": 80, "height": 80}
        self.assertFalse(is_inside(child, parent))

    def test_exact_fit(self):
        box = {"x": 0, "y": 0, "width": 80, "height": 80}
        self.assertTrue(is_inside(box, box))

    @given(
        st.integers(min_value=0, max_value=500),
        st.integers(min_value=0, max_value=500),
        st.integers(min_value=50, max_value=800),
        st.integers(min_value=50, max_value=800),
    )
    @settings(max_examples=40, deadline=None)
    def test_self_contained_when_same_box(self, x, y, w, h):
        box = {"x": x, "y": y, "width": w, "height": h}
        self.assertTrue(is_inside(box, box))

    @given(
        st.integers(min_value=0, max_value=200),
        st.integers(min_value=0, max_value=200),
    )
    @settings(max_examples=30, deadline=None)
    def test_child_outside_when_shifted_beyond(self, dx, dy):
        parent = {"x": 0, "y": 0, "width": 100, "height": 100}
        # Default child size 80x80; place so bottom-right exceeds parent
        child = {"x": 100 + dx, "y": 100 + dy}
        self.assertFalse(is_inside(child, parent))


class TestBuildMxgraphXml(unittest.TestCase):
    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            asyncio.run(build_mxgraph_xml([], [], []))

    @patch(
        "services.diagram_builder.fetch_icon_from_n8n",
        new_callable=AsyncMock,
        return_value='<svg xmlns="http://www.w3.org/2000/svg"></svg>',
    )
    def test_nodes_and_edges_produce_mxgraph(self, _icon):
        groups = [
            {
                "id": "g1",
                "name": "VPC",
                "type": "vpc",
                "x": 0,
                "y": 0,
                "width": 400,
                "height": 300,
            }
        ]
        nodes = [
            {"id": "n1", "name": "ec2", "x": 40, "y": 40},
            {"id": "n2", "name": "rds", "x": 200, "y": 40},
        ]
        edges = [{"source": "n1", "target": "n2"}]
        xml = asyncio.run(build_mxgraph_xml(groups, nodes, edges))
        self.assertIn("<mxGraphModel>", xml)
        self.assertIn('id="g1"', xml)
        self.assertIn('id="n1"', xml)
        self.assertIn('source="n1" target="n2"', xml)
        # Nested node should reference group as parent when inside
        self.assertIn('parent="g1"', xml)

    @patch(
        "services.diagram_builder.fetch_icon_from_n8n",
        new_callable=AsyncMock,
        return_value="<svg></svg>",
    )
    def test_edge_omitted_without_endpoints(self, _icon):
        nodes = [{"id": "n1", "name": "ec2", "x": 0, "y": 0}]
        xml = asyncio.run(
            build_mxgraph_xml(None, nodes, [{"source": "n1"}])  # missing target
        )
        self.assertNotIn("edge_", xml)


if __name__ == "__main__":
    unittest.main()
