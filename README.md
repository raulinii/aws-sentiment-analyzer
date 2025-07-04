# AWS Sentiment Detection Pipeline

This project implements an automated sentiment detection system using AWS services. When a `.txt` file is uploaded to an S3 bucket, it triggers a Lambda function that analyzes the text using the Claude Instant model (via Bedrock), stores the result in DynamoDB, and sends an alert via SNS if the sentiment is negative.

## Architecture Overview

**Services Used:**
- **Amazon S3**: Stores incoming `.txt` files.
- **AWS Lambda**: Executes the sentiment detection logic.
- **Amazon Bedrock**: Provides access to the Claude model.
- **Amazon DynamoDB**: Stores results of the sentiment analysis.
- **Amazon SNS**: Sends alert notifications for negative sentiment.

## How It Works

1. A `.txt` file is uploaded to an S3 bucket.
2. This triggers a Lambda function via an S3 event notification.
3. The function:
   - Downloads and reads the file.
   - Sends a prompt to the Claude model through Bedrock.
   - Receives the sentiment result (`positive`, `neutral`, or `negative`).
   - Stores the result in a DynamoDB table.
   - Sends an SNS alert if the sentiment is negative.

## Environment Variables

Make sure your Lambda function has the following environment variables set:

- `REGION` — your AWS region (e.g. `us-west-2`)
- `DYNAMODB_TABLE` — name of your DynamoDB table
- `SNS_TOPIC_ARN` — ARN of the SNS topic to publish alerts to

## Deployment

This project was deployed using:

- AWS Console
- AWS CLI (`aws configure` to get started)
- Manual setup of Lambda triggers and IAM roles

All Python logic is in `lambda_function.py`. You can zip and deploy it using:

```bash
zip lambda_function.zip lambda_function.py