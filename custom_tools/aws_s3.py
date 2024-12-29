import os
from phi.tools import Toolkit

try:
    import boto3
except ImportError:
    raise ImportError("boto3 is required for S3Tool. Please install it using `pip install boto3`.")


class MissingAWSCredentialsError(Exception):
    """Custom exception raised when AWS credentials are missing."""
    pass


class S3Tool(Toolkit):
    """
    A tool for interacting with AWS S3 buckets. This tool provides functionalities for:
    - Listing all buckets in the AWS account.
    - Listing objects within a specific bucket.
    - Uploading files to a bucket.
    - Deleting files from a bucket.
    - Creating new buckets.
    - Deleting existing buckets.

    Methods:
    - list_buckets: Returns a list of all S3 buckets in the AWS account.
    - list_objects: Returns a list of all objects in a specific S3 bucket.
    - upload_file: Uploads a file to a specified S3 bucket with a given key.
    - delete_file: Deletes a specific object from a specified S3 bucket.
    - create_bucket: Creates a new S3 bucket in a specified region.
    - delete_bucket: Deletes an existing S3 bucket.
    """

    name: str = "S3Tool"
    description: str = "A tool for interacting with AWS S3 buckets"

    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize the S3Tool with a specific AWS region.

        Args:
            region_name (str): The AWS region to use for S3 operations. Default is 'us-east-1'.

        Raises:
            MissingAWSCredentialsError: If AWS access keys and secret keys are not found in the environment.
        """
        super().__init__()

        # Check if AWS credentials are present in the environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not aws_access_key or not aws_secret_key:
            raise MissingAWSCredentialsError(
                "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set as environment variables. "
                "Please set these variables and try again."
            )

        # Initialize the S3 client
        self.client = boto3.client("s3", region_name=region_name)

        # Registering the tool's methods
        self.register(self.list_buckets)
        self.register(self.list_objects)
        self.register(self.upload_file)
        self.register(self.delete_file)

    def list_buckets(self) -> str:
        """
        Lists all S3 buckets in the AWS account.

        Returns:
            str: A comma-separated list of bucket names or an error message if the operation fails.

        Example:
            "Available S3 buckets: bucket1, bucket2, bucket3"
        """
        try:
            response = self.client.list_buckets()
            buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]
            return f"Available S3 buckets: {', '.join(buckets)}"
        except Exception as e:
            return f"Error listing buckets: {str(e)}"

    def list_objects(self, bucket_name: str) -> str:
        """
        Lists all objects in a specific S3 bucket.

        Args:
            bucket_name (str): The name of the bucket to list objects from.

        Returns:
            str: A comma-separated list of object keys or an error message if the operation fails.

        Example:
            "Objects in bucket 'example-bucket': file1.txt, image2.jpg"

        Error:
            If the bucket does not exist or is inaccessible, an error message is returned.
        """
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name)
            objects = [obj["Key"] for obj in response.get("Contents", [])]
            return f"Objects in bucket '{bucket_name}': {', '.join(objects)}"
        except Exception as e:
            return f"Error listing objects in bucket '{bucket_name}': {str(e)}"

    def upload_file(self, file_path: str, bucket_name: str, object_name: str) -> str:
        """
        Uploads a file to a specific S3 bucket.

        Args:
            file_path (str): The local path to the file to be uploaded.
            bucket_name (str): The name of the S3 bucket to upload the file to.
            object_name (str): The key (name) of the object in the bucket.

        Returns:
            str: A success message or an error message if the operation fails.

        Example:
            "File 'example.txt' successfully uploaded to bucket 'example-bucket' as 'example.txt'"

        Error:
            If the file does not exist or the upload fails, an error message is returned.
        """
        try:
            self.client.upload_file(file_path, bucket_name, object_name)
            return f"File '{file_path}' successfully uploaded to bucket '{bucket_name}' as '{object_name}'"
        except Exception as e:
            return f"Error uploading file: {str(e)}"

    def delete_file(self, bucket_name: str, object_name: str) -> str:
        """
        Deletes a specific object from an S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            object_name (str): The key (name) of the object to be deleted.

        Returns:
            str: A success message or an error message if the operation fails.

        Example:
            "File 'example.txt' successfully deleted from bucket 'example-bucket'"

        Error:
            If the object does not exist or the deletion fails, an error message is returned.
        """
        try:
            self.client.delete_object(Bucket=bucket_name, Key=object_name)
            return f"File '{object_name}' successfully deleted from bucket '{bucket_name}'"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    
    def create_bucket(self, bucket_name: str, region_name: str = None) -> str:
        """
        Creates a new S3 bucket.

        Args:
            bucket_name (str): The name of the bucket to create.
            region_name (str): The AWS region where the bucket will be created.
                Defaults to the region specified in the tool initialization.

        Returns:
            str: A success message or an error message if the operation fails.

        Example:
            "Bucket 'my-new-bucket' successfully created in region 'us-east-1'"

        Error:
            If the bucket creation fails, an error message is returned.
        """
        try:
            # If region is specified, create bucket in that region
            create_bucket_params = {"Bucket": bucket_name}
            if region_name and region_name != "us-east-1":
                create_bucket_params["CreateBucketConfiguration"] = {
                    "LocationConstraint": region_name
                }
            self.client.create_bucket(**create_bucket_params)
            return f"Bucket '{bucket_name}' successfully created in region '{region_name or 'us-east-1'}'"
        except Exception as e:
            return f"Error creating bucket '{bucket_name}': {str(e)}"

    def delete_bucket(self, bucket_name: str) -> str:
        """
        Deletes an existing S3 bucket.

        Args:
            bucket_name (str): The name of the bucket to delete.

        Returns:
            str: A success message or an error message if the operation fails.

        Example:
            "Bucket 'example-bucket' successfully deleted"

        Error:
            If the bucket deletion fails, an error message is returned.
        """
        try:
            self.client.delete_bucket(Bucket=bucket_name)
            return f"Bucket '{bucket_name}' successfully deleted"
        except Exception as e:
            return f"Error deleting bucket '{bucket_name}': {str(e)}"

    
