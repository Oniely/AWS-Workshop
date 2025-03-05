import urllib
import csv
import codecs
import boto3

def batch_create_products(event, context):
    print("file uploaded trigger")
    print(event)
    
    print("Extract file location from event payload")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    filename = key.split("/")[-1]
    localFilename = f'/tmp/{filename}'
    s3_client = boto3.client('s3', region_name='us-east-2')
    
    print("downloaded file to /tmp folder")
    s3_client.download_file(bucket, key, localFilename)
    
    print("reading CSV file and looping it over...")
    
    with open(localFilename, 'r') as f:
        csv_reader = csv.DictReader(f)
        required_keys = ["product_id", "product_name", "price", "quantity"]
        table_name = "products-oniely"
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table(table_name)
        for row in csv_reader:
            table.put_item(
               Item=row
            )
    
    print("All done!")
    return {}
    
def batch_delete_products(event, context):
    print("file uploaded trigger")
    print(event)
    
    print("Extract file location from event payload")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    filename = key.split("/")[-1]
    localFilename = f'/tmp/{filename}'
    s3_client = boto3.client('s3', region_name='us-east-2')
    
    print("downloaded file to /tmp folder")
    s3_client.download_file(bucket, key, localFilename)
    
    print("reading CSV file and looping it over...")
    
    with open(localFilename, 'r') as f:
        csv_reader = csv.DictReader(f)
        required_keys = ["product_id"]
        table_name = "products-oniely"
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table(table_name)
        for data in csv_reader:
            print(data)
            item = data.get('Item')
            table.delete_item(
               Key={'product_id': data['product_id']}
            )
    
    print("All done!")
    return {}