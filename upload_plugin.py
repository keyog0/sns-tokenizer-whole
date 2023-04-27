import boto3
import os

def upload_s3(s3_path,file,os_path):
    bucket = os.getenv("AWS_S3_BUCKET")
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(os_path+'/'+file, bucket, f"tokenizer{s3_path}/"+file)
    
def main():
    print("[INFO]------Elasticsearch 플러그인 S3업로드 진행------")
    upload_s3(
        s3_path="/plugin",
        file="elasticsearch-7.17.4-okt-2.1.0-plugin.zip",
        os_path="/output"
    )
    upload_s3(
        s3_path="/jar",
        file="open-korean-text-2.1.0.jar",
        os_path="/output"
    )
    print("[COMPLETE]------Elasticsearch 플러그인 S3업로드 완료------")
    
if __name__ == '__main__':
    main()