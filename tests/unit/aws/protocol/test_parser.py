from urllib.parse import urlencode

from botocore.serialize import QuerySerializer

from localstack.aws.api import HttpRequest
from localstack.aws.protocol.parser import QueryRequestParser
from localstack.aws.spec import load_service
from localstack.utils.common import to_bytes


def test_query_parser():
    """Basic test for the QueryParser with a simple example (SQS SendMessage request)."""
    parser = QueryRequestParser(load_service("sqs"))
    request = HttpRequest(
        body=to_bytes(
            "Action=SendMessage&Version=2012-11-05&"
            "QueueUrl=http%3A%2F%2Flocalhost%3A4566%2F000000000000%2Ftf-acc-test-queue&"
            "MessageBody=%7B%22foo%22%3A+%22bared%22%7D&"
            "DelaySeconds=2"
        ),
        method="POST",
        headers={},
        path="",
    )
    operation, params = parser.parse(request)
    assert operation.name == "SendMessage"
    assert params == {
        "QueueUrl": "http://localhost:4566/000000000000/tf-acc-test-queue",
        "MessageBody": '{"foo": "bared"}',
        "DelaySeconds": 2,
    }


def test_query_parser_flattened_map():
    """Simple test with a flattened map (SQS SetQueueAttributes request)."""
    parser = QueryRequestParser(load_service("sqs"))
    request = HttpRequest(
        body=to_bytes(
            "Action=SetQueueAttributes&Version=2012-11-05&"
            "QueueUrl=http%3A%2F%2Flocalhost%3A4566%2F000000000000%2Ftf-acc-test-queue&"
            "Attribute.1.Name=DelaySeconds&"
            "Attribute.1.Value=10&"
            "Attribute.2.Name=MaximumMessageSize&"
            "Attribute.2.Value=131072&"
            "Attribute.3.Name=MessageRetentionPeriod&"
            "Attribute.3.Value=259200&"
            "Attribute.4.Name=ReceiveMessageWaitTimeSeconds&"
            "Attribute.4.Value=20&"
            "Attribute.5.Name=RedrivePolicy&"
            "Attribute.5.Value=%7B%22deadLetterTargetArn%22%3A%22arn%3Aaws%3Asqs%3Aus-east-1%3A80398EXAMPLE%3AMyDeadLetterQueue%22%2C%22maxReceiveCount%22%3A%221000%22%7D&"
            "Attribute.6.Name=VisibilityTimeout&Attribute.6.Value=60"
        ),
        method="POST",
        headers={},
        path="",
    )
    operation, params = parser.parse(request)
    assert operation.name == "SetQueueAttributes"
    assert params == {
        "QueueUrl": "http://localhost:4566/000000000000/tf-acc-test-queue",
        "Attributes": {
            "DelaySeconds": "10",
            "MaximumMessageSize": "131072",
            "MessageRetentionPeriod": "259200",
            "ReceiveMessageWaitTimeSeconds": "20",
            "RedrivePolicy": '{"deadLetterTargetArn":"arn:aws:sqs:us-east-1:80398EXAMPLE:MyDeadLetterQueue","maxReceiveCount":"1000"}',
            "VisibilityTimeout": "60",
        },
    }


def test_query_parser_non_flattened_map():
    """Simple test with a flattened map (SQS SetQueueAttributes request)."""
    parser = QueryRequestParser(load_service("sns"))
    request = HttpRequest(
        body=to_bytes(
            "Action=SetEndpointAttributes&"
            "EndpointArn=arn%3Aaws%3Asns%3Aus-west-2%3A123456789012%3Aendpoint%2FGCM%2Fgcmpushapp%2F5e3e9847-3183-3f18-a7e8-671c3a57d4b3&"
            "Attributes.entry.1.key=CustomUserData&"
            "Attributes.entry.1.value=My+custom+userdata&"
            "Version=2010-03-31&"
            "AUTHPARAMS"
        ),
        method="POST",
        headers={},
        path="",
    )
    operation, params = parser.parse(request)
    assert operation.name == "SetEndpointAttributes"
    assert params == {
        "Attributes": {"CustomUserData": "My custom userdata"},
        "EndpointArn": "arn:aws:sns:us-west-2:123456789012:endpoint/GCM/gcmpushapp/5e3e9847-3183-3f18-a7e8-671c3a57d4b3",
    }


def test_query_parser_non_flattened_list_structure():
    """Simple test with a non-flattened list structure (CloudFormation CreateChangeSet)."""
    parser = QueryRequestParser(load_service("cloudformation"))
    request = HttpRequest(
        body=to_bytes(
            "Action=CreateChangeSet&"
            "ChangeSetName=SampleChangeSet&"
            "Parameters.member.1.ParameterKey=KeyName&"
            "Parameters.member.1.UsePreviousValue=true&"
            "Parameters.member.2.ParameterKey=Purpose&"
            "Parameters.member.2.ParameterValue=production&"
            "StackName=arn:aws:cloudformation:us-east-1:123456789012:stack/SampleStack/1a2345b6-0000-00a0-a123-00abc0abc000&"
            "UsePreviousTemplate=true&"
            "Version=2010-05-15&"
            "X-Amz-Algorithm=AWS4-HMAC-SHA256&"
            "X-Amz-Credential=[Access-key-ID-and-scope]&"
            "X-Amz-Date=20160316T233349Z&"
            "X-Amz-SignedHeaders=content-type;host&"
            "X-Amz-Signature=[Signature]"
        ),
        method="POST",
        headers={},
        path="",
    )
    operation, params = parser.parse(request)
    assert operation.name == "CreateChangeSet"
    assert params == {
        "StackName": "arn:aws:cloudformation:us-east-1:123456789012:stack/SampleStack/1a2345b6-0000-00a0-a123-00abc0abc000",
        "UsePreviousTemplate": True,
        "Parameters": [
            {"ParameterKey": "KeyName", "UsePreviousValue": True},
            {"ParameterKey": "Purpose", "ParameterValue": "production"},
        ],
        "ChangeSetName": "SampleChangeSet",
    }


def test_query_parser_non_flattened_list_structure_changed_name():
    """Simple test with a non-flattened list structure where the name of the list differs from the shape's name
    (CloudWatch PutMetricData)."""
    parser = QueryRequestParser(load_service("cloudwatch"))
    request = HttpRequest(
        body=to_bytes(
            "Action=PutMetricData&"
            "Version=2010-08-01&"
            "Namespace=TestNamespace&"
            "MetricData.member.1.MetricName=buffers&"
            "MetricData.member.1.Unit=Bytes&"
            "MetricData.member.1.Value=231434333&"
            "MetricData.member.1.Dimensions.member.1.Name=InstanceType&"
            "MetricData.member.1.Dimensions.member.1.Value=m1.small&"
            "AUTHPARAMS"
        ),
        method="POST",
        headers={},
        path="",
    )
    operation, params = parser.parse(request)
    assert operation.name == "PutMetricData"
    assert params == {
        "MetricData": [
            {
                "Dimensions": [{"Name": "InstanceType", "Value": "m1.small"}],
                "MetricName": "buffers",
                "Unit": "Bytes",
                "Value": 231434333.0,
            }
        ],
        "Namespace": "TestNamespace",
    }


def test_query_parser_flattened_list_structure():
    """Simple test with a flattened list of structures."""
    parser = QueryRequestParser(load_service("sqs"))
    request = HttpRequest(
        body=to_bytes(
            "Action=DeleteMessageBatch&"
            "Version=2012-11-05&"
            "QueueUrl=http%3A%2F%2Flocalhost%3A4566%2F000000000000%2Ftf-acc-test-queue&"
            "DeleteMessageBatchRequestEntry.1.Id=bar&"
            "DeleteMessageBatchRequestEntry.1.ReceiptHandle=foo&"
            "DeleteMessageBatchRequestEntry.2.Id=bar&"
            "DeleteMessageBatchRequestEntry.2.ReceiptHandle=foo"
        ),
        method="POST",
        headers={},
        path="",
    )
    operation, params = parser.parse(request)
    assert operation.name == "DeleteMessageBatch"
    assert params == {
        "QueueUrl": "http://localhost:4566/000000000000/tf-acc-test-queue",
        "Entries": [{"Id": "bar", "ReceiptHandle": "foo"}, {"Id": "bar", "ReceiptHandle": "foo"}],
    }


def _test_query_parser_botocore_integration_test(service: str, action: str, **kwargs):
    # Load the appropriate service
    service = load_service(service)
    # Use the serializer from botocore to serialize the request params
    serializer = QuerySerializer()
    serialized_request = serializer.serialize_to_request(kwargs, service.operation_model(action))

    # Serialize the body as query parameter
    serialized_request["body"] = urlencode(serialized_request["body"])

    # Use our parser to parse the serialized body
    parser = QueryRequestParser(service)
    operation_model, parsed_request = parser.parse(serialized_request)

    # Check if the result is equal to the initial params
    assert parsed_request == kwargs


def test_query_parser_sqs_with_botocore():
    _test_query_parser_botocore_integration_test(
        service="sqs",
        action="SendMessage",
        QueueUrl="string",
        MessageBody="string",
        DelaySeconds=123,
        MessageAttributes={
            "string": {
                "StringValue": "string",
                "BinaryValue": b"bytes",
                "StringListValues": [
                    "string",
                ],
                "BinaryListValues": [
                    b"bytes",
                ],
                "DataType": "string",
            }
        },
        MessageSystemAttributes={
            "string": {
                "StringValue": "string",
                "BinaryValue": b"bytes",
                "StringListValues": [
                    "string",
                ],
                "BinaryListValues": [
                    b"bytes",
                ],
                "DataType": "string",
            }
        },
        MessageDeduplicationId="string",
        MessageGroupId="string",
    )


def test_query_parser_cloudformation_with_botocore():
    _test_query_parser_botocore_integration_test(
        service="cloudformation",
        action="CreateStack",
        StackName="string",
        TemplateBody="string",
        TemplateURL="string",
        Parameters=[
            {
                "ParameterKey": "string",
                "ParameterValue": "string",
                "UsePreviousValue": True,
                "ResolvedValue": "string",
            },
        ],
        DisableRollback=False,
        RollbackConfiguration={
            "RollbackTriggers": [
                {"Arn": "string", "Type": "string"},
            ],
            "MonitoringTimeInMinutes": 123,
        },
        TimeoutInMinutes=123,
        NotificationARNs=[
            "string",
        ],
        Capabilities=[
            "CAPABILITY_IAM",
        ],
        ResourceTypes=[
            "string",
        ],
        RoleARN="string",
        OnFailure="DO_NOTHING",
        StackPolicyBody="string",
        StackPolicyURL="string",
        Tags=[
            {"Key": "string", "Value": "string"},
        ],
        ClientRequestToken="string",
        EnableTerminationProtection=False,
    )


# TODO Add additional tests (or even automate the creation)
# - Go to the Boto3 Docs (https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/index.html)
# - Look for boto3 request syntax definition for services that use the protocol you want to test
# - Take request syntax, remove the "or" ("|") and call the helper function with these named params
