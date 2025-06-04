'''
Copyright (C) 2019 Medtronic Diabetes.
All Rights Reserved.
This software is the confidential and proprietary information of
Medtronic Diabetes.  Confidential Information.  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Medtronic Diabetes.
'''
import os
import sys
import traceback
import logging
import yaml
from time import sleep, gmtime, strftime
from argparse import ArgumentParser
import boto3
from pathlib import Path
sys.path.append('common_modules/')
sys.path.append('../common_modules/')
sys.path.append('../../common_modules/')
import common_modules

s3_client=boto3.client('s3')
s3=boto3.resource('s3')
cloudformation = boto3.resource('cloudformation')
config_folder="config/"
s3_artifacts_loc="config/s3-artifacts/"
template_folder="core/templates/"

#Create Initial bucket to upload basic templates
def create_bucket(args,data) :

    for bucket in data["buckets"]:
        bkt_name=next(iter(bucket))
        ssm_key=bucket[bkt_name]['ssm-key']
        export_name=bucket[bkt_name]['export-name']

        if (s3.Bucket(bkt_name) in s3.buckets.all())==True:
            print("Bucket "+bkt_name+" Creation Failed\n")
            print("Bucket "+bkt_name+" already exists\n")
            logging.info("Bucket "+bkt_name+" already exists\n")
        else:
            try:
                input_params = dict()
                input_params['keyName'] = args.keyName
                s3_template_url = args.s3TemplateURL
                print("\nCreating bucket "+bkt_name)
                response = cloudformation.create_stack(
                    StackName = bkt_name,
                    TemplateURL = s3_template_url,
                    Parameters=[
                            {'ParameterKey': 'BucketName','ParameterValue': bkt_name},
                            {'ParameterKey': 'SSMKey','ParameterValue': ssm_key},
                            {'ParameterKey': 'KeyName','ParameterValue': input_params['keyName']},
                            {'ParameterKey': 'ExportName','ParameterValue': export_name}
                        ]
                )
                common_modules.get_stack_status(cloudformation, bkt_name)
                print("Bucket "+bkt_name+" created successfully\n")
            except Exception as e:
                logging.error("\nBucket "+bkt_name+" Creation Failed:\n"+str(e))
                traceback.print_exc()
                raise OSError("\nBucket "+bkt_name+" Creation Failed:\n")

def upload_files(args,data):
    for bkt_name in data["files"].keys():
        if (s3.Bucket(bkt_name) in s3.buckets.all())==True:
            for file_name in data["files"][bkt_name]:
                try:
                    print("Uploading File "+file_name+" to bucket "+bkt_name)
                    if os.path.isfile(s3_artifacts_loc+file_name):
                        s3_client.upload_file(s3_artifacts_loc+file_name,bkt_name,file_name)
                        print("File "+file_name+" is uploaded to bucket "+bkt_name)
                    else:
                        print("Path "+file_name+" is not a file. skipping upload...")
                except Exception as e:
                    print("\nFailed to upload file "+file_name)
                    logging.error("\nFailed to upload file "+file_name+str(e))
                    traceback.print_exc()
                    raise OSError("\nFailed to upload file "+file_name)
        else:
            print("\nBucket  "+bkt_name+" does not exist. Can not upload file")

def upload_folders(args,data):
    for bkt_name in data["folders"].keys():
        if (s3.Bucket(bkt_name) in s3.buckets.all())==True:
            for folder in data["folders"][bkt_name]:
                try:
                    print("Uploading Folder "+folder+" to bucket "+bkt_name)
                    files_list = list(Path("./"+s3_artifacts_loc+folder).rglob("*"))
                    for file_name in files_list:
                        if os.path.isfile(str(file_name)):
                            s3_client.upload_file(str(file_name),bkt_name,str(file_name))
                    print("Folder "+folder+" is uploaded to bucket "+bkt_name)
                except Exception as e:
                    print("\nFailed to upload Folder "+folder)
                    logging.error("\nFailed to upload Folder "+folder+str(e))
                    traceback.print_exc()
                    raise OSError("\nFailed to upload Folder "+folder)
        else:
            print("\nBucket  "+bkt_name+" does not exist. Can not upload file")
    



if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("--configfilepath", dest="configfilepath", required=True, metavar="<configfilepath>",
                        help="Path of config file for S3 bucket creation")
    parser.add_argument("--s3TemplateURL", dest="s3TemplateURL", required=True, metavar="<s3TemplateURL>",
                        help="Template URL for S3 Bucket Creation")
    parser.add_argument("--AWSRegion", dest="region", required=True, metavar="<AWSRegion>",
                        help="AWS Region")
    parser.add_argument("--keyName", dest="keyName", required=True, metavar="<keyName>",
                        help="KMS Key Name for bucketencryption")
    parser.add_argument("--createBucket", dest="createBucket", required=True, metavar="<createBucket>",default="True",
                        choices=["True","False"],help="Choice to create Buckets")
    parser.add_argument("--uploadFiles", dest="uploadFiles", required=True, metavar="<uploadFiles>",default="True",
                        choices=["True","False"],help="Choice to upload Files")
    parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<logLevel>",default="INFO",
                        help="Logging level INFO|DEBUG|ERROR|WARNING")
    args = parser.parse_args()


    logDir = os.getcwd() + "/log"
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    logFile = logDir +  '/'+os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'
    logging.basicConfig(filename=logFile, filemode='w', level=args.logLevel, format='%(asctime)s   %(levelname)s     %(message)s')

    file= open(config_folder+args.configfilepath)
    data=yaml.safe_load(file)

    if args.createBucket == 'True':
        create_bucket(args,data)

    if args.uploadFiles == 'True': 
        upload_files(args,data) 
        if "folders" in data.keys():
            upload_folders(args,data)
