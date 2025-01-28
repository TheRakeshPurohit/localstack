# LocalStack Resource Provider Scaffolding v2
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional, TypedDict

import localstack.services.cloudformation.provider_utils as util
from localstack.services.cloudformation.resource_provider import (
    OperationStatus,
    ProgressEvent,
    ResourceProvider,
    ResourceRequest,
)


class LambdaEventInvokeConfigProperties(TypedDict):
    FunctionName: Optional[str]
    Qualifier: Optional[str]
    DestinationConfig: Optional[DestinationConfig]
    Id: Optional[str]
    MaximumEventAgeInSeconds: Optional[int]
    MaximumRetryAttempts: Optional[int]


class OnSuccess(TypedDict):
    Destination: Optional[str]


class OnFailure(TypedDict):
    Destination: Optional[str]


class DestinationConfig(TypedDict):
    OnFailure: Optional[OnFailure]
    OnSuccess: Optional[OnSuccess]


REPEATED_INVOCATION = "repeated_invocation"


class LambdaEventInvokeConfigProvider(ResourceProvider[LambdaEventInvokeConfigProperties]):
    TYPE = "AWS::Lambda::EventInvokeConfig"  # Autogenerated. Don't change
    SCHEMA = util.get_schema_path(Path(__file__))  # Autogenerated. Don't change

    def create(
        self,
        request: ResourceRequest[LambdaEventInvokeConfigProperties],
    ) -> ProgressEvent[LambdaEventInvokeConfigProperties]:
        """
        Create a new resource.

        Primary identifier fields:
          - /properties/Id

        Required properties:
          - FunctionName
          - Qualifier

        Create-only properties:
          - /properties/FunctionName
          - /properties/Qualifier

        Read-only properties:
          - /properties/Id



        """
        model = request.desired_state
        lambda_client = request.aws_client_factory.lambda_

        lambda_client.put_function_event_invoke_config(**model)
        model["Id"] = str(uuid.uuid4())  # TODO: not actually a UUIDv4

        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resource_model=model,
            custom_context=request.custom_context,
        )

    def read(
        self,
        request: ResourceRequest[LambdaEventInvokeConfigProperties],
    ) -> ProgressEvent[LambdaEventInvokeConfigProperties]:
        """
        Fetch resource information


        """
        raise NotImplementedError

    def delete(
        self,
        request: ResourceRequest[LambdaEventInvokeConfigProperties],
    ) -> ProgressEvent[LambdaEventInvokeConfigProperties]:
        """
        Delete a resource


        """
        model = request.desired_state
        lambda_client = request.aws_client_factory.lambda_

        lambda_client.delete_function_event_invoke_config(
            FunctionName=model["FunctionName"], Qualifier=model["Qualifier"]
        )

        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resource_model=model,
            custom_context=request.custom_context,
        )

    def update(
        self,
        request: ResourceRequest[LambdaEventInvokeConfigProperties],
    ) -> ProgressEvent[LambdaEventInvokeConfigProperties]:
        """
        Update a resource


        """
        raise NotImplementedError
