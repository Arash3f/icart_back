import boto3
import logging
import os

from jdatetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

host = "localhost"
port = "5432"
dbname = "icart_prod"
user = "postgres_prod"
password = "postgres_prod"
address = "/home/ubuntu/fastApi/backup"
backup_name = "icart_prod.bak"
endpoint_url = "https://s3.ir-thr-at1.arvanstorage.ir"
aws_access_key_id = "c3f2a815-14c0-4d3a-bc42-898e6605676c"
aws_secret_access_key = (
    "2a1e686ae1cce27ea3f58b078484ca09e9e095390933a425f9469caee002729a"
)
bucket_name = "icart"
file_path = "{}/{}".format(address, backup_name)

os.system(
    "docker exec -it icart-back-database-prod pg_dump 'host={} port={} dbname={} user={} password={}' > {}".format(
        host,
        port,
        dbname,
        user,
        password,
        file_path,
    ),
)

version = 1

now = datetime.now()

if now.hour <= 6 and now.hour > 24:
    version = 1
elif now.hour <= 12 and now.hour > 6:
    version = 2
elif now.hour <= 24 and now.hour > 12:
    version = 3
else:
    version = 4

try:
    s3_resource = boto3.resource(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    bucket = s3_resource.Bucket(bucket_name)
    file_path = "{}/{}".format(address, backup_name)
    with open(file_path, "rb") as file:
        bucket.put_object(
            ACL="private",
            Body=file,
            Key=backup_name + "-v" + str(version),
        )
except Exception as exc:
    logging.error(exc)

# os.system("rm -rf {}".format(file_path))
