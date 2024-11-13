import os
import unittest
from unittest import mock
import boto3
from importlib import import_module


class SimpleTest(unittest.TestCase):
    """Simple test listing buckets using the moto library to mock s3 client responses."""
    def setUp(self) -> None:
        modified_environ = {
            k: v for k, v in os.environ.items() if k not in "AWS_PROFILE"
        }
        with mock.patch.dict(os.environ, modified_environ, clear=True):
            mock_aws = import_module("moto").mock_aws
            self.mock_aws = mock_aws()
            self.mock_aws.start()
            self.s3_client = boto3.client("s3")
            self.s3_client.create_bucket(Bucket="Test-Bucket")

    def tearDown(self) -> None:
        self.mock_aws.stop()

    def test(self):
        response = self.s3_client.list_buckets()
        bucket_names = [bucket["Name"] for bucket in response["Buckets"]]
        self.assertIn("Test-Bucket", bucket_names)
