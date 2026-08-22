"""Unit tests for pricing_client and offer parser."""

from __future__ import annotations

import json
import os
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from cost.pricing_client import PriceMiss, PriceUnsupported, fetch_hourly, supports_official_hourly
from cost.pricing_offer_parser import parse_on_demand_hourly

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "aws_ec2_offer_snippet.json"


class TestPricingOfferParser(unittest.TestCase):
    def setUp(self):
        with _FIXTURE.open(encoding="utf-8") as f:
            self.offer = json.load(f)

    def test_parse_ec2_t3_micro(self):
        hourly = parse_on_demand_hourly(
            self.offer,
            product_family="Compute Instance",
            attribute_filters={
                "instanceType": "t3.micro",
                "operatingSystem": "Linux",
                "tenancy": "Shared",
                "preInstalledSw": "NA",
                "capacitystatus": "Used",
            },
        )
        self.assertEqual(hourly, Decimal("0.0104000000"))

    def test_parse_miss_when_no_match(self):
        hourly = parse_on_demand_hourly(
            self.offer,
            product_family="Compute Instance",
            attribute_filters={"instanceType": "m5.24xlarge"},
        )
        self.assertIsNone(hourly)


class TestPricingClient(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("COST_PRICING_STUB", None)

    def test_stub_mode(self):
        os.environ["COST_PRICING_STUB"] = "1"
        result = fetch_hourly("aws", "AmazonEC2", "us-east-1")
        self.assertEqual(result.kind, "hit")
        self.assertEqual(result.hourly, Decimal("0.12"))

    def test_gcp_without_api_key_miss(self):
        os.environ.pop("COST_PRICING_STUB", None)
        os.environ.pop("GCP_BILLING_API_KEY", None)
        result = fetch_hourly("gcp", "ComputeEngine", "us-central1")
        self.assertIsInstance(result, PriceMiss)

    def test_azure_unconfigured_sku_miss(self):
        result = fetch_hourly("azure", "Compute", "eastus")
        self.assertIsInstance(result, PriceMiss)

    def test_azure_aks_supported(self):
        self.assertTrue(supports_official_hourly("AzureKubernetesService"))

    def test_s3_supported_with_assumed_storage(self):
        os.environ.pop("COST_PRICING_STUB", None)
        self.assertTrue(supports_official_hourly("AmazonS3"))

    @patch("cost.pricing_client.fetch_hourly_via_sdk")
    @patch("cost.pricing_client.use_sdk_enabled")
    def test_sdk_path_before_bulk(self, sdk_enabled_mock, sdk_fetch_mock):
        os.environ.pop("COST_PRICING_STUB", None)
        os.environ["COST_PRICING_USE_SDK"] = "1"
        sdk_enabled_mock.return_value = True
        sdk_fetch_mock.return_value = Decimal("0.0104")
        result = fetch_hourly("aws", "AmazonEC2", "us-east-1")
        self.assertEqual(result.kind, "hit")
        self.assertEqual(result.hourly, Decimal("0.0104"))
        self.assertEqual(result.source, "aws_sdk")
        sdk_fetch_mock.assert_called_once_with("AmazonEC2", "us-east-1")

    @patch("cost.pricing_client._download_offer")
    def test_live_parse_path(self, download_mock):
        os.environ.pop("COST_PRICING_STUB", None)
        with _FIXTURE.open(encoding="utf-8") as f:
            download_mock.return_value = json.load(f)
        result = fetch_hourly("aws", "AmazonEC2", "us-east-1")
        self.assertEqual(result.kind, "hit")
        self.assertEqual(result.hourly, Decimal("0.0104000000"))

    def test_rejects_non_allowlisted_url(self):
        from cost.pricing_client import _host_allowed

        self.assertFalse(_host_allowed("https://evil.example.com/offers/v1.0/aws/index.json"))
        self.assertTrue(
            _host_allowed(
                "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-1/index.json"
            )
        )
        self.assertTrue(_host_allowed("https://prices.azure.com/api/retail/prices"))


if __name__ == "__main__":
    unittest.main()
