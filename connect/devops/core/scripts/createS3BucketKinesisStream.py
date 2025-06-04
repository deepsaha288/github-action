'''
Copyright (C) 2019 Medtronic Diabetes.
All Rights Reserved.
This software is the confidential and proprietary information of
Medtronic Diabetes.  Confidential Information.  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Medtronic Diabetes.

python3 -W ignore core/scripts/createS3BucketKinesisStream.py --s3BucketName ble-applogs-failure-horizon  --KmsKeyARN arn:aws:kms:eu-central-1:812470574530:key/81126344-db4e-4743-bfd9-2b4073e5facf --AWSRegion eu-central-1 --logLevel INFO

python3 -W ignore core/scripts/createS3BucketKinesisStream.py --s3BucketName mobile-applogs-es-records-horizon  --KmsKeyARN arn:aws:kms:eu-central-1:812470574530:key/d917e766-a30c-4817-b95d-e8aa1941ff5d --AWSRegion eu-central-1 --logLevel INFO

'''
import os
import sys
import traceback
import logging
import yaml
from time import sleep, gmtime, strftime
from argparse import ArgumentParser
import boto3

s3_client=boto3.client('s3')
s3=boto3.resource('s3')

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("--s3BucketName", dest="s3BucketName", required=True, metavar="<s3BucketName>",
                        help="Name of the s3 bucket to be created")

    parser.add_argument("--KmsKeyARN", dest="KmsKeyARN", required=True, metavar="<KmsKeyARN>",
                        help="AWS Managed KMS Key ARN aws/s3")
    parser.add_argument("--AWSRegion", dest="region", required=True, metavar="<AWSRegion>",
                        help="AWS Region")
    parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<logLevel>",default="INFO",
                        help="Logging level INFO|DEBUG|ERROR|WARNING")
    args = parser.parse_args()


    logDir = os.getcwd() + "/log"
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    logFile = logDir +  '/'+os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'
    logging.basicConfig(filename=logFile, filemode='w', level=args.logLevel, format='%(asctime)s   %(levelname)s     %(message)s')

    try:
        print("\nCreating s3 Bucket "+args.s3BucketName)

        # Added this condition because this is an artifact of the underlying S3 API that it doesn't accept us-east-1.
        # To create an S3 bucket in us-east-1 you can just not specify any CreateBucketConfiguration
        # if args.region == 'us-east-1':
        #     s3.create_bucket(Bucket=args.s3BucketName)
        # else:
        s3.create_bucket(Bucket=args.s3BucketName,CreateBucketConfiguration={'LocationConstraint': args.region})
        sleep(10)
        s3_client.put_bucket_encryption(
            Bucket=args.s3BucketName,
            ServerSideEncryptionConfiguration={
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'aws:kms',
                        'KMSMasterKeyID': args.KmsKeyARN
                    }
                },
            ]
            }
        )
        s3_client.put_public_access_block(
                Bucket=args.s3BucketName,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
        print("S3 Bucket "+args.s3BucketName+" for Kinesis Stream created successfully\n")

    except Exception as e:
        logging.error("CF Bucket "+args.s3BucketName+" Creation Failed\n"+str(e))
        traceback.print_exc()
        raise OSError("CF Bucket "+args.s3BucketName+" Creation Failed\n")
