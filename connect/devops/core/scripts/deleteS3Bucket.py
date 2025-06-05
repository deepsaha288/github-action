import boto3
import argparse
import logging

def delete_bucket(bucket_name, region):
    s3 = boto3.resource('s3', region_name=region)
    bucket = s3.Bucket(bucket_name)

    print(f"Deleting all objects in the bucket '{bucket_name}'...")
    bucket.objects.all().delete()

    print(f"Deleting the bucket '{bucket_name}'...")
    bucket.delete()

    print(f"S3 Bucket '{bucket_name}' deleted successfully in region '{region}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--s3BucketName", required=True, help="Name of the S3 bucket to delete")
    parser.add_argument("--stackName", required=True, help="CloudFormation Stack Name (not used, for tracking/logging)")
    parser.add_argument("--AWSRegion", required=True, help="AWS Region of the S3 bucket")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Deleting S3 bucket: {args.s3BucketName}, stack: {args.stackName}, region: {args.AWSRegion}")

    delete_bucket(args.s3BucketName, args.AWSRegion)
