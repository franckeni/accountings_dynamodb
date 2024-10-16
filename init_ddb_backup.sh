#! /bin/bash

export AWS_PROFILE=default

DYNAMODB_ENDPOINT_URL=http://localhost:4566
TABLE_NAME=dev-accountings-erp-api
AWS_REGION=$(aws configure get region)

function dynamodb_list_tables() {
  response=$(aws dynamodb list-tables \
    --endpoint-url $DYNAMODB_ENDPOINT_URL \
    --region $AWS_REGION  \
    --output text \
    --query "TableNames")

  local error_code=${?}

  if [[ $error_code -ne 0 ]]; then
    aws_cli_error_log $error_code
    errecho "ERROR: AWS reports batch-write-item operation failed.$response"
    return 1
  fi

  echo "$response" | tr -s "[:space:]" "\n"

  return 0
}

function errecho() {
  printf "%s\n" "$*" 1>&2
}

function aws_cli_error_log() {
  local err_code=$1
  errecho "Error code : $err_code"
  if [ "$err_code" == 1 ]; then
    errecho "  One or more S3 transfers failed."
  elif [ "$err_code" == 2 ]; then
    errecho "  Command line failed to parse."
  elif [ "$err_code" == 130 ]; then
    errecho "  Process received SIGINT."
  elif [ "$err_code" == 252 ]; then
    errecho "  Command syntax invalid."
  elif [ "$err_code" == 253 ]; then
    errecho "  The system environment or configuration was invalid."
  elif [ "$err_code" == 254 ]; then
    errecho "  The service returned an error."
  elif [ "$err_code" == 255 ]; then
    errecho "  255 is a catch-all error."
  fi

  return 0
}


RESULT=$(dynamodb_list_tables)


# if [ "$DYNAMODB_IS_READY" = 1 ]; then
if [[ $RESULT =~ $TABLE_NAME ]] 
then
  echo "Table already exist in database"
else 
  echo "table name not founded, Creating DynamoDB table ..."
  source .venv/bin/activate
  python3 $DYNAMODB_PYTHON_PATH $TABLE_NAME $DYNAMODB_ENDPOINT_URL $AWS_REGION

  i="0"
  # while ! nc -z "$DYNAMODB_HOST" "$DYNAMODB_PORT"; do
  while ! [[ $RESULT =~ $TABLE_NAME ]]; do
    #sleep 0.1

    echo $i

    i=$[$i+1]
    if [ "$i" == "5" ]; then
      break
    fi
    RESULT=$(dynamodb_list_tables)
  done

  echo "database is ready"
  aws ddb put $TABLE_NAME --endpoint-url $DYNAMODB_ENDPOINT_URL --region $AWS_REGION  "$(<$DYNAMODB_BACKUP_PATH)"
fi

exec "$@"