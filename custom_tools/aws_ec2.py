import os
from phi.tools import Toolkit

try:
    import boto3
except ImportError:
    raise ImportError("boto3 is required for EC2Tool. Please install it using `pip install boto3`.")

class MissingAWSCredentialsError(Exception):
    """Custom exception raised when AWS credentials are missing."""
    pass

class EC2Tool(Toolkit):
    """
    A tool for managing AWS EC2 instances. This tool provides functionalities for:
    - Listing EC2 instances and their statuses.
    - Starting an EC2 instance.
    - Stopping an EC2 instance.
    - Checking the status of an EC2 instance.
    - Terminating an EC2 instance.
    - Creating new EC2 instances with specific configurations.

    Methods:
    - list_instances: Lists all EC2 instances in the specified region along with their current states.
    - start_instance: Starts a specific EC2 instance by its instance ID.
    - stop_instance: Stops a specific EC2 instance by its instance ID.
    - check_instance_status: Gets the current status of a specific EC2 instance by its instance ID.
    - terminate_instance: Terminates a specific EC2 instance by its instance ID.
    - create_instance: Creates a new EC2 instance using a specified AMI, instance type, and optional configuration.

    Notes:
    - Ensure that AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) 
      are available in the environment variables before using this tool.
    - The 'create_instance' method requires a valid AMI ID and instance type. 
      Key pair and security group are optional but recommended for better control.
    - This tool operates in the specified AWS region. The default region is 'us-east-1'.

    """

    name: str = "EC2Tool"
    description: str = "A tool for managing AWS EC2 instances"

    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize the EC2Tool with a specific AWS region.

        Args:
            region_name (str): The AWS region to use for EC2 operations. Default is 'us-east-1'.
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
        
        self.client = boto3.client("ec2", region_name=region_name)
        self.register(self.list_instances)
        self.register(self.start_instance)
        self.register(self.stop_instance)
        self.register(self.check_instance_status)
        self.register(self.terminate_instance)
        self.register(self.create_instance)


    def list_instances(self) -> str:
        """
        Lists all EC2 instances in the specified region, along with their current state.

        Returns:
            str: A formatted list of instance IDs and their states.
        """
        try:
            response = self.client.describe_instances()
            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append(
                        f"Instance ID: {instance['InstanceId']}, State: {instance['State']['Name']}"
                    )
            return "\n".join(instances) if instances else "No EC2 instances found."
        except Exception as e:
            return f"Error listing instances: {str(e)}"

    def start_instance(self, instance_id: str) -> str:
        """
        Starts an EC2 instance.

        Args:
            instance_id (str): The ID of the instance to start.

        Returns:
            str: A success message or an error message if the operation fails.
        """
        try:
            self.client.start_instances(InstanceIds=[instance_id])
            return f"Instance {instance_id} is starting."
        except Exception as e:
            return f"Error starting instance {instance_id}: {str(e)}"

    def stop_instance(self, instance_id: str) -> str:
        """
        Stops an EC2 instance.

        Args:
            instance_id (str): The ID of the instance to stop.

        Returns:
            str: A success message or an error message if the operation fails.
        """
        try:
            self.client.stop_instances(InstanceIds=[instance_id])
            return f"Instance {instance_id} is stopping."
        except Exception as e:
            return f"Error stopping instance {instance_id}: {str(e)}"

    def check_instance_status(self, instance_id: str) -> str:
        """
        Checks the status of an EC2 instance.

        Args:
            instance_id (str): The ID of the instance to check.

        Returns:
            str: The current status of the instance.
        """
        try:
            response = self.client.describe_instance_status(InstanceIds=[instance_id])
            if not response["InstanceStatuses"]:
                return f"Instance {instance_id} is stopped or does not exist."
            state = response["InstanceStatuses"][0]["InstanceState"]["Name"]
            return f"Instance {instance_id} is {state}."
        except Exception as e:
            return f"Error checking status of instance {instance_id}: {str(e)}"
        
    def create_instance(self, image_id: str, instance_type: str, key_name: str = None, security_group: str = None, min_count: int = 1, max_count: int = 1) -> str:
        """
        Creates a new EC2 instance.

        Args:
            image_id (str): The ID of the AMI to use for the instance.
            instance_type (str): The type of instance to create (e.g., 't2.micro').
            key_name (str, optional): The name of the key pair for SSH access.
            security_group (str, optional): The name of the security group to associate with the instance.
            min_count (int, optional): The minimum number of instances to create. Default is 1.
            max_count (int, optional): The maximum number of instances to create. Default is 1.

        Returns:
            str: A success message with the instance ID(s) or an error message if the operation fails.
        """
        try:
            # Prepare the parameters for the instance creation
            launch_params = {
                "ImageId": image_id,
                "InstanceType": instance_type,
                "MinCount": min_count,
                "MaxCount": max_count,
            }

            if key_name:
                launch_params["KeyName"] = key_name
            if security_group:
                launch_params["SecurityGroups"] = [security_group]

            # Create the instance(s)
            response = self.client.run_instances(**launch_params)

            # Collect the instance IDs of the launched instances
            instance_ids = [instance["InstanceId"] for instance in response["Instances"]]
            return f"Instance(s) created successfully. Instance ID(s): {', '.join(instance_ids)}"
        except Exception as e:
            return f"Error creating instance: {str(e)}"


    def terminate_instance(self, instance_id: str) -> str:
        """
        Terminates an EC2 instance.

        Args:
            instance_id (str): The ID of the instance to terminate.

        Returns:
            str: A success message or an error message if the operation fails.
        """
        try:
            self.client.terminate_instances(InstanceIds=[instance_id])
            return f"Instance {instance_id} is terminating."
        except Exception as e:
            return f"Error terminating instance {instance_id}: {str(e)}"
