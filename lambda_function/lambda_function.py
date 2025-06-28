# boto3 is used to allow python code to interact with AWS services (in this case S3, Bedrock, DynamoDB)
# json is used to send and parse data
# os is used for environment variables
import json
import boto3
import os

def lambda_handler(event, context):
    print("EVENT TRIGGERED:", json.dumps(event))

    # 1. Get file info from S3 event
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        print(f"File triggered from S3 bucket: {bucket}, key: {key}")
    except Exception as e:
        print("Error extracting S3 info:", str(e))
        return {"statusCode": 400, "body": "Invalid S3 trigger event."}

    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=key)
        text = obj['Body'].read().decode('utf-8')
        print("S3 file content successfully read.")
    except Exception as e:
        print("Error reading from S3:", str(e))
        return {"statusCode": 500, "body": "Failed to read file from S3."}

    # 2. Call Bedrock for sentiment
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=os.environ['REGION'])
        prompt = f"\n\nHuman: What is the sentiment of this text? Respond with 'positive', 'neutral', or 'negative'.\n\n{text}\n\nAssistant:"
        print("Sending prompt to Claude:", prompt)

        response = bedrock.invoke_model(
            modelId="anthropic.claude-instant-v1",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 30,
                "temperature": 0
            }),
            contentType="application/json",
            accept="application/json"
        )

        response_body = response['body'].read().decode('utf-8')
        result = json.loads(response_body)["completion"]
        print("Claude response:", result)
    except Exception as e:
        print("Error calling Bedrock:", str(e))
        return {"statusCode": 500, "body": "Failed to get response from Bedrock."}

    # 3. Store in DynamoDB
    try:
        print("Initializing DynamoDB resource...")
        dynamo = boto3.resource('dynamodb', region_name=os.environ['REGION'])
        table = dynamo.Table(os.environ['DYNAMODB_TABLE'])
        print("DynamoDB table reference acquired.")

        print(f"Putting item into DynamoDB: File={key}, Sentiment={result.strip()}")
        table.put_item(Item={'File': key, 'Sentiment': result.strip()})
        print("Successfully stored in DynamoDB.")
    except Exception as e:
        print("ERROR writing to DynamoDB:", str(e))
        return {"statusCode": 500, "body": "Failed to write to DynamoDB."}

    # 4. Send alert if sentiment is negative
    try:
        if 'negative' in result.lower():
            print("Negative sentiment detected. Sending SNS alert.")
            sns = boto3.client('sns')
            sns.publish(
                TopicArn=os.environ['SNS_TOPIC_ARN'],
                Message=f'Negative sentiment detected in file: {key}',
                Subject='Sentiment Alert'
            )
            print("SNS alert sent.")
    except Exception as e:
        print("ERROR sending SNS alert:", str(e))

    return {"statusCode": 200, "body": f"Processed {key} with sentiment: {result.strip()}"}
