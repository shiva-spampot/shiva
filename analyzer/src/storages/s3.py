from typing import Any
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
from storages.base import BaseStorage
import logging as logger

logger.getLogger(__name__)


class S3Storage(BaseStorage):

    def __init__(
        self,
        bucket_name,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        region_name=None,
        file_path_in_s3="",
    ):
        """
        Initializes S3Storage

        :param bucket_name: Name of the S3 bucket.
        :param aws_access_key_id: Optional, AWS access key id.
        :param aws_secret_access_key: Optional, AWS secret access key.
        :param aws_session_token: Optional, session token for temporary credentials.
        :param region_name: AWS region.
        :param file_path_in_s3: Optional default path (folder) in S3 to store files.

        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.file_path_in_s3 = file_path_in_s3.strip("/")

        if aws_access_key_id and aws_secret_access_key:
            client_kwargs = {
                aws_access_key_id: aws_access_key_id,
                aws_secret_access_key: aws_secret_access_key,
                region_name: self.region_name,
            }
            if aws_session_token:
                client_kwargs["aws_session_token"] = aws_session_token

            self.s3_client = boto3.client("s3", **client_kwargs)

        else:
            self.s3_client = boto3.client("s3", region_name=self.region_name)

    def save(self, filename: str, data: Any) -> str:
        """Saves data to an S3 bucket."""
        try:
            if self.file_path_in_s3:
                key = f"{self.file_path_in_s3}/{filename}"
            else:
                key = filename

            self.s3_client.put_object(
                Body=data,
                Bucket=self.bucket_name,
                Key=key,
            )

            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        except NoCredentialsError:
            logger.error("Credentials not available for AWS S3.")
        except PartialCredentialsError:
            logger.error("Incomplete credentials provided.")
        except Exception as e:
            logger.error(f"Error saving data to S3: {str(e)}", exc_info=True)
