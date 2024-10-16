import logging
import os
import sys
import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_dynamodb_table(table_name: str, dynamodb: DynamoDBServiceResource):

    return dynamodb.create_table(
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "gsi1_pk", "AttributeType": "S"},
            {"AttributeName": "gsi1_sk", "AttributeType": "S"},
            {"AttributeName": "gsi2_pk", "AttributeType": "S"},
            {"AttributeName": "gsi2_sk", "AttributeType": "S"},
        ],
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "gsi1",
                "KeySchema": [
                    {"AttributeName": "gsi1_pk", "KeyType": "HASH"},
                    {"AttributeName": "gsi1_sk", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            },
            {
                "IndexName": "gsi2",
                "KeySchema": [
                    {"AttributeName": "gsi2_pk", "KeyType": "HASH"},
                    {"AttributeName": "gsi2_sk", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "ALL",
                },
            },
        ],
    )


def existing_or_create_dynamodb_table(
    table_name: str, dynamodb: DynamoDBServiceResource
):
    try:
        table: Table = None

        existing_tables = [table.name for table in dynamodb.tables.all()]

        if table_name in existing_tables:
            logger.info("tABLE %s ALREADY EXIST", table_name)
        else:
            table = create_dynamodb_table(table_name, dynamodb)
            logger.info("\nCreated table %s.", table.name)
    except ClientError:
        logger.exception("\nCouldn't create Table")
        raise
    else:
        return table


if __name__ == "__main__":
    table_name = sys.argv[1]
    endpoint_url = os.getenv("DYNAMODB_URL", sys.argv[2])
    region_name = os.getenv("AWS_DEFAULT_REGION", sys.argv[3])

    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        region_name=region_name
    )

    existing_or_create_dynamodb_table(table_name, dynamodb)
