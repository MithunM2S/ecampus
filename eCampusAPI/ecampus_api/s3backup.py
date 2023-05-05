import boto3
import os
import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists(os.path.join(BASE_DIR, '.env')):
    environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

bucket = os.environ.get('S3_BUCKET_NAME', False) 
prefix = os.environ.get('PREFIX', False)
dir_path = os.environ.get('DB_BACKUP_PATH', False)
aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY_ID', False)
aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY', False)

s3_client = boto3.client('s3', aws_access_key_id= aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

os.system('find ' + dir_path + ' -name "*.dump.gz" -mtime +7 -exec rm {} \;')

def s3_upload_backup():
    for db_file in os.listdir(dir_path):
        s3_client.upload_file(os.path.join(dir_path, db_file), bucket, prefix + db_file)

def s3_delete_existing_backup():
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = response.get('Contents', None)
    if contents:
        for object in contents:
            s3_client.delete_object(Bucket=bucket, Key=object['Key'])

s3_delete_existing_backup()
s3_upload_backup()