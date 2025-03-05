import string
import random
import csv
import json
import boto3

def generate_code(prefix, string_length):
  letters = string.ascii_uppercase
  return prefix + ''.join(random.choice(letters) for i in range(string_length))

def receive_message_from_sqs(event, context):
    print("file uploaded trigger")
    print(event)
    
    fieldnames=["product_id", "product_name", "brand_name", "price", "quantity"]
    
    file_randomized_prefix = generate_code("pycon_", 8)
    file_name = f'/tmp/product_created_{file_randomized_prefix}.csv'
    bucket = "products-sqsbucket-oniely"
    object_name = f'product_created_{file_randomized_prefix}.csv'
    
    
    with open(file_name, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for payload in event["Records"]:
            print(f"Payload: {payload}")
            json_payload = json.loads(payload["body"])
            writer.writerow(json_payload)

   
    s3_client = boto3.client('s3')
    s3_client.upload_file(file_name, bucket, object_name)
        
    print(f"File uploaded to S3: s3://{bucket}/{object_name}")
    print("All done!")
    
    return {}