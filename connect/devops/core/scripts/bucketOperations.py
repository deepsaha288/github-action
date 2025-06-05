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
import time
from time import gmtime, strftime
from argparse import ArgumentParser
import boto3
sys.path.append('common_modules/')
sys.path.append('../common_modules/')
sys.path.append('../../common_modules/')
import common_modules




def get_stack_status(cloudformation, stack_name):
    
    ret = 0
    logging.info( "Checking for status of stack: %s", stack_name)

    while True:
        stack = cloudformation.Stack(stack_name)
        #print stack
        if (stack.stack_status.find("CREATE_COMPLETE") != -1) :
            logging.info( "Stack creation completed...")
            ret = 0
            break
        elif (stack.stack_status.find("CREATE_IN_PROGRESS") != -1) :
            logging.info( "Stack creation is in progres... ")
            time.sleep(10)
        else:
            logging.error("Stack creation failed with below status: %s", stack.stack_status)
            print % stack.stack_status
            logging.error("Stack creation failed with below status: %s", stack.stack_status)
            ret  = 1
            raise   OSError("Stack creation failed with below status: %s" % stack.stack_status)
            break
    
    return ret

def get_bucket_file_list(s3, bucketName):
    fileList = []
    bucketObjList = s3.list_objects(Bucket=bucketName)
    if 'Contents' in bucketObjList:
        for bucketObj in bucketObjList['Contents']:
            fileList.append(bucketObj['Key'])
    return fileList

def loadProperties(file_path, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file.
    """
    props = {}
    with open(file_path, "rt") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"') 
                props[key] = value 
    return props


# Startup code excution from here
if __name__ == '__main__':

	
    parser = ArgumentParser()

    parser.add_argument("--bucketName", dest="bucketName", required=True, metavar="<bucketName>",
                        help="Bucket name where to transfer files")
    parser.add_argument("--operation", dest="operation", required=True, metavar="<operation>",
            help="Operation: create/delete/clean")
    parser.add_argument("--AWSRegion", dest="region", required=True, metavar="<AWSRegion>",
                        help="AWS Region")
    parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<LogLevel>",
                        help="Logging level INFO|DEBUG|ERROR|WARNING")

    args = parser.parse_args()
    try:       

        logLevel = args.logLevel
        if logLevel is None:
            logLevel = 'INFO'
        
        input_params = dict()

        input_params['operation'] = args.operation
        input_params['bucketName'] = args.bucketName
        input_params['region'] =  args.region
        

        baseDir = os.getcwd()
        logDir = baseDir + "/log"
        if not os.path.exists(logDir):
            os.makedirs(logDir)

        logFile = logDir +  '/'+os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'

        logging.basicConfig(filename=logFile, filemode='w', level=logLevel, format='%(asctime)s   %(levelname)s     %(message)s')


        logging.info("Input parameter details are as below:") 
        logging.info(input_params)

        logging.info("**************************************************")
        if input_params['operation'].lower() == "create" :
            logging.info("Creating S3 bucket: %s" , input_params['bucketName'])
        elif input_params['operation'].lower() == "delete" :
            logging.info("Deleting S3 bucket: %s" , input_params['bucketName'])
        elif input_params['operation'].lower() == "clean" :
            logging.info("Removing all files in S3 bucket: %s" , input_params['bucketName'])
        else:
            logging.error("Invalid operation [%s] specified, exiting... ", input_params['operation'])
            traceback.print_exc()
            raise OSError("Invalid operation [%s] specified, exiting... ", input_params['operation'])
            sys.exit(-1)
        logging.info("**************************************************")


        s3 = boto3.client('s3')
        
        if input_params['operation'].lower() == "create" :
            response = s3.create_bucket(Bucket=input_params['bucketName'],CreateBucketConfiguration={'LocationConstraint': input_params['region']})
            logging.info(response)
        elif input_params['operation'].lower() == "delete" :
            response = s3.delete_bucket(Bucket=input_params['bucketName'])
            logging.info(response)
        else:
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(input_params['bucketName'])
            for key in bucket.objects.all():
                logging.info("Removing file [%s] from bucket [%s]", key.key, input_params['bucketName'])
                key.delete()

    except Exception as exp:
        logging.error("Caught Exception %s", str(exp))
        traceback.print_exc(file=sys.stdout)
        logging.error('exiting ....')    
        raise OSError("Caught Exception %s", str(exp))
        sys.exit(-1)   
