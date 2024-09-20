from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_sqs as sqs,
)
from constructs import Construct

class MichaelJinShunLeongQuestion1Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "MichaelJinShunLeongQuestion1Queue",
            fifo=True,
        )

        post_lambda = _lambda.Function(
            self, "PostLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            environment={
                'QUEUE_URL': queue.queue_url
            },
            code=_lambda.Code.from_inline(
                """
import json
import boto3
import os
import uuid

sqs = boto3.client('sqs')
queue_url = os.environ['QUEUE_URL']

def handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {})
        
        # generate a unique deduplication ID
        deduplication_id = str(uuid.uuid4())

        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(query_params),  # send the query parameters as the message body
            MessageGroupId='default',  # required for FIFO queues
            MessageDeduplicationId=deduplication_id
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'messageId': response['MessageId']})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

                """
            ),
        )

        get_lambda = _lambda.Function(
            self, "GetLambdaHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            environment={
                'QUEUE_URL': queue.queue_url
            },
            code=_lambda.Code.from_inline(
                """
import json
import boto3
import os

sqs = boto3.client('sqs')
queue_url = os.environ['QUEUE_URL']

def handler(event, context):
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            VisibilityTimeout=10,
            WaitTimeSeconds=5
        )
        
        messages = response.get('Messages', [])
        
        if messages:
            message = messages[0]
            
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps(json.loads(message['Body']))
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No messages in the queue'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
                """
            ),
        )

        queue.grant_send_messages(post_lambda)
        queue.grant_consume_messages(get_lambda)

        api = apigateway.RestApi(self, "SQSApi",
            rest_api_name="API for SQS",
            description="API to send and receive messages from SQS"
        )

        post_integration = apigateway.LambdaIntegration(post_lambda)
        api.root.add_resource("send_message").add_method("POST", post_integration)

        get_integration = apigateway.LambdaIntegration(get_lambda)
        api.root.add_resource("get_message").add_method("GET", get_integration)
