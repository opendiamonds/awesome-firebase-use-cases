"""Unit tests for diagram_extractor."""

import unittest

from cost.diagram_extractor import extract_priceable_cells


class TestDiagramExtractor(unittest.TestCase):
    def test_empty_label_uses_res_icon(self):
        xml = (
            '<mxGraphModel><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>'
            '<mxCell id="ec" value="" '
            'style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elasticache;" '
            'vertex="1" parent="1"/>'
            "</root></mxGraphModel>"
        )
        cells = extract_priceable_cells(xml)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0].label_plain, "elasticache")

    def test_bare_ampersand_in_label_does_not_500(self):
        xml = (
            '<mxGraphModel><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>'
            '<mxCell id="g" value="Analytics & Blockchain" '
            'style="shape=mxgraph.aws4.group;" vertex="1" parent="1"/>'
            '<mxCell id="ec2" value="EC2" '
            'style="shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;" '
            'vertex="1" parent="1"/>'
            "</root></mxGraphModel>"
        )
        cells = extract_priceable_cells(xml)
        labels = {c.label_plain for c in cells}
        self.assertIn("EC2", labels)


if __name__ == "__main__":
    unittest.main()
