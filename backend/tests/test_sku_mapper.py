"""Unit tests for sku_mapper."""

import unittest

from cost.sku_mapper import map_cell


class TestSkuMapper(unittest.TestCase):
    def test_res_icon_ec2(self):
        result = map_cell(
            "EC2 Instances App servers",
            "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.ec2;",
        )
        self.assertEqual(result.kind, "unique")
        assert result.candidate is not None
        self.assertEqual(result.candidate.sku, "AmazonEC2")

    def test_res_icon_rds_without_rds_label(self):
        result = map_cell(
            "Aurora PostgreSQL",
            "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.rds;",
        )
        self.assertEqual(result.kind, "unique")
        assert result.candidate is not None
        self.assertEqual(result.candidate.sku, "AmazonRDS")

    def test_res_icon_elb(self):
        result = map_cell(
            "Elastic Load Balancing",
            "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.elastic_load_balancing;",
        )
        self.assertEqual(result.kind, "unique")
        assert result.candidate is not None
        self.assertEqual(result.candidate.sku, "AWSELB")

    def test_a1_uppercase_label_without_aws4_style(self):
        """A1 產圖：shape=image + 全大寫 label，無 resIcon／aws4。"""
        style = "shape=image;image=data:image/svg+xml,abc"
        cases = [
            ("EC2", "AmazonEC2"),
            ("RDS", "AmazonRDS"),
            ("S3", "AmazonS3"),
            ("ALB", "AWSELB"),
            ("ROUTE53", "AmazonRoute53"),
            ("ROUTE 53", "AmazonRoute53"),
            ("CLOUDFRONT", "AmazonCloudFront"),
            ("WAF", "AWSWAF"),
            ("ELASTICACHE", "AmazonElastiCache"),
            ("AURORA", "AmazonRDS"),
            ("ECS", "AmazonECS"),
            ("EKS", "AmazonEKS"),
            ("LAMBDA", "AWSLambda"),
            ("CLOUDWATCH", "AmazonCloudWatch"),
            ("NAT GATEWAY", "AmazonEC2NatGateway"),
            ("NATGATEWAY", "AmazonEC2NatGateway"),
            ("NAT", "AmazonEC2NatGateway"),
            ("API GATEWAY", "AmazonApiGateway"),
            ("APIGATEWAY", "AmazonApiGateway"),
            ("GLUE", "AWSGlue"),
            ("AWS GLUE", "AWSGlue"),
            ("SAGEMAKER", "AmazonSageMaker"),
            ("AMAZON SAGEMAKER", "AmazonSageMaker"),
            ("ATHENA", "AmazonAthena"),
            ("AMAZON ATHENA", "AmazonAthena"),
        ]
        for label, sku in cases:
            with self.subTest(label=label):
                result = map_cell(label, style)
                self.assertEqual(result.kind, "unique", label)
                assert result.candidate is not None
                self.assertEqual(result.candidate.sku, sku, label)

    def test_gcp_label_maps(self):
        style = "shape=image;image=data:image/svg+xml,abc"
        cases = [
            ("CLOUD RUN", "CloudRun"),
            ("CLOUDRUN", "CloudRun"),
            ("cloud run", "CloudRun"),
            ("GKE", "KubernetesEngine"),
            ("CLOUD SQL", "CloudSQL"),
            ("CLOUDSQL", "CloudSQL"),
            ("CLOUD STORAGE", "CloudStorage"),
            ("CLOUDSTORAGE", "CloudStorage"),
            ("CLOUD DNS", "CloudDNS"),
            ("CLOUDDNS", "CloudDNS"),
            ("CLOUD LOAD BALANCING", "Networking"),
            ("COMPUTE ENGINE", "ComputeEngine"),
            ("COMPUTEENGINE", "ComputeEngine"),
            ("CLOUD ARMOR", "CloudArmor"),
            ("CLOUDARMOR", "CloudArmor"),
            ("CLOUD CDN", "CloudCDN"),
            ("CLOUDCDN", "CloudCDN"),
            ("APIGEE", "Apigee"),
            ("Apigee", "Apigee"),
            ("BIGQUERY", "BigQuery"),
            ("BigQuery", "BigQuery"),
            ("bigquery", "BigQuery"),
            ("FIRESTORE", "Firestore"),
            ("Firestore", "Firestore"),
            ("firestore", "Firestore"),
            ("VERTEX AI", "VertexAI"),
            ("VERTEXAI", "VertexAI"),
            ("SECRET MANAGER", "SecretManager"),
            ("SECRETMANAGER", "SecretManager"),
            ("GOOGLE CLOUD OBSERVABILITY", "CloudObservability"),
            ("CLOUD OBSERVABILITY", "CloudObservability"),
            ("CLOUD MONITORING", "CloudObservability"),
        ]
        for label, sku in cases:
            with self.subTest(label=label):
                result = map_cell(label, style)
                self.assertEqual(result.kind, "unique", label)
                assert result.candidate is not None
                self.assertEqual(result.candidate.sku, sku, label)
                self.assertEqual(result.candidate.cloud, "gcp", label)

    def test_short_labels_do_not_substring_false_positive(self):
        style = "shape=image;image=data:image/svg+xml,abc"
        # 舊邏輯：API⊂Apigee、LB⊂ALB、SQL⊂Cloud SQL、CDN⊂Cloud CDN
        for label in ("API", "LB", "SQL", "CDN", "DNS"):
            with self.subTest(label=label):
                self.assertEqual(map_cell(label, style).kind, "none", label)

    def test_load_balancer_not_cross_cloud_ambiguous(self):
        style = "shape=image;image=data:image/svg+xml,abc"
        self.assertEqual(map_cell("LOAD BALANCER", style).kind, "none")
        alb = map_cell("APPLICATION LOAD BALANCER", style)
        self.assertEqual(alb.kind, "unique")
        assert alb.candidate is not None
        self.assertEqual(alb.candidate.sku, "AWSELB")
        gcp = map_cell("CLOUD LOAD BALANCER", style)
        self.assertEqual(gcp.kind, "unique")
        assert gcp.candidate is not None
        self.assertEqual(gcp.candidate.sku, "Networking")

    def test_azure_label_maps(self):
        style = "shape=image;image=data:image/svg+xml,abc"
        cases = [
            ("AKS", "AzureKubernetesService"),
            ("APPLICATION GATEWAY", "ApplicationGateway"),
            ("AZURE BLOB STORAGE", "AzureBlobStorage"),
            ("AZURE COSMOS DB", "AzureCosmosDB"),
            ("AZURE SQL DATABASE", "AzureSQLDatabase"),
            ("AZURE KEY VAULT", "KeyVault"),
            ("AZURE MONITOR", "AzureMonitor"),
            ("AZURE FRONT DOOR", "AzureFrontDoor"),
            ("AZURE CDN", "AzureCDN"),
            ("WEB APPLICATION FIREWALL", "AzureFirewall"),
            ("LOG ANALYTICS", "LogAnalytics"),
            ("RECOVERY SERVICES VAULT", "AzureBackup"),
        ]
        for label, sku in cases:
            with self.subTest(label=label):
                result = map_cell(label, style)
                self.assertEqual(result.kind, "unique", label)
                assert result.candidate is not None
                self.assertEqual(result.candidate.sku, sku, label)
                self.assertEqual(result.candidate.cloud, "azure", label)

    def test_azure_aks_not_confused_with_eks(self):
        result = map_cell("AKS", "shape=image;image=data:image/svg+xml,abc")
        self.assertEqual(result.kind, "unique")
        assert result.candidate is not None
        self.assertEqual(result.candidate.cloud, "azure")


if __name__ == "__main__":
    unittest.main()
