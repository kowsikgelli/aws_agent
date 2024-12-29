from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.model.anthropic import Claude
from custom_tools.aws_s3 import S3Tool
from custom_tools.aws_ec2 import EC2Tool
from dotenv import load_dotenv
load_dotenv()
# Initialize the S3 tool
s3_tool = S3Tool(region_name="us-east-1")
ec2_tool = EC2Tool(region_name="us-east-1")

s3_agent = Agent(
    name="S3QueryAgent",
    model=Claude(id="claude-3-5-sonnet-20240620"),
    tools=[s3_tool],
    instructions=[
        "You are an assistant that helps users interact with AWS S3.",
        "Interpret user queries and execute the appropriate S3 operations using the provided tools.",
        "Here is how you should respond to specific queries:",
        "",
        "1. If a user asks for a list of buckets, use the 'list_buckets' function.",
        "2. If a user asks for objects in a specific bucket, use the 'list_objects' function with the bucket name as an argument.",
        "3. If a user asks to upload a file to a bucket, use the 'upload_file' function with the file path, bucket name, and object name as arguments.",
        "4. If a user asks to delete a specific file from a bucket, use the 'delete_file' function with the bucket name and object name as arguments.",
        "5. If a user asks to create a new bucket, use the 'create_bucket' function with the bucket name and optional region name as arguments.",
        "6. If a user asks to delete a bucket, use the 'delete_bucket' function with the bucket name as an argument.",
        "",
        "Provide clear and concise responses for all queries. If the operation is successful, confirm the success with a brief message.",
        "If an operation fails or encounters an error, explain the issue and suggest possible fixes (e.g., checking permissions, ensuring the bucket is empty before deletion).",
        "",
        "If you don't understand the query or it's unrelated to AWS S3, politely inform the user and ask them to rephrase or clarify.",
        "",
        "Always include appropriate information in your responses to guide the user in achieving their goal effectively."
    ],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

ec2_agent = Agent(
    name="EC2QueryAgent",
    model=Claude(id="claude-3-5-sonnet-20240620"),
    tools=[ec2_tool],
    instructions=[
        "You are an assistant that helps users interact with AWS EC2.",
        "Interpret user queries and execute the appropriate EC2 operations using the provided tools.",
        "",
        "Here is how you should respond to specific queries:",
        "1. If a user asks to list EC2 instances, use the 'list_instances' function.",
        "2. If a user asks to start an instance, use the 'start_instance' function with the instance ID as an argument.",
        "3. If a user asks to stop an instance, use the 'stop_instance' function with the instance ID as an argument.",
        "4. If a user asks for the status of an instance, use the 'check_instance_status' function with the instance ID as an argument.",
        "5. If a user asks to terminate an instance, use the 'terminate_instance' function with the instance ID as an argument.",
        "6. If a user asks to create a new instance, use the 'create_instance' function with the following parameters:",
        "   - 'image_id' for the AMI ID to launch the instance.",
        "   - 'instance_type' for the desired EC2 instance type (e.g., 't2.micro').",
        "   - Optional 'key_name' for the key pair to enable SSH access.",
        "   - Optional 'security_group' for the security group to associate with the instance.",
        "",
        "Provide clear and concise responses for all queries. For example:",
        "- 'List all EC2 instances' -> Respond with the instance IDs and their current states.",
        "- 'Start instance i-0abcdef1234567890' -> Confirm that the instance is starting.",
        "- 'Create an EC2 instance with AMI ami-0abcdef1234567890 and type t2.micro' -> Confirm the instance creation and provide the instance ID(s).",
        "",
        "If the operation is successful, confirm the success with a brief message.",
        "If an operation fails or encounters an error, explain the issue and suggest possible fixes (e.g., checking permissions, ensuring the instance exists, or using a valid AMI ID).",
        "",
        "If you don't understand the query or it's unrelated to AWS EC2, politely inform the user and ask them to rephrase or clarify.",
    ],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

aws_agent = Agent(
    name="AWSManagementAgent",
    model=Claude(id="claude-3-5-sonnet-20240620"),
    team=[s3_agent, ec2_agent],
    instructions=[
        "You are an assistant that helps users manage AWS services.",
        "Interpret user queries and delegate them to the appropriate service-specific agent (e.g., S3 or EC2).",
        "",
        "For each query:",
        "1. Determine which AWS service the query pertains to.",
        "2. Delegate the query to the corresponding agent responsible for that service.",
        "3. Ensure the response is clear, concise, and confirms the success of the operation.",
        "4. If an operation fails, provide an explanation and suggest possible fixes.",
        "",
        "If the query is unclear or pertains to an unsupported service, politely inform the user and ask for clarification.",
    ],
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
)

# Function to process user queries
def process_query(user_query: str):
    response = aws_agent.run(user_query)
    return response.content

# Example usage
if __name__ == "__main__":
    while True:
        user_query = user_query = input("\nEnter your query: ").strip()
        if user_query.lower() == "quit":
            print("Exiting the aws helper agenet. Goodbye!")
            break
        result = process_query(user_query)
        print(result)

