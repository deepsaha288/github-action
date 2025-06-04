'''
Copyright (C) 2019 Medtronic Diabetes.
All Rights Reserved.
This software is the confidential and proprietary information of
Medtronic Diabetes.  Confidential Information.  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Medtronic Diabetes.

python3 -W ignore core/scripts/deployIaaSKmsKey.py --stackName ${STACKNAME_PREFIX}-Core-IaaS-KMS --templateUrl  ${S3_BUCKET_URL}/janus-iaas-kms-key.yaml --UserArn ${USER_ARN} --IAASEC2Arn {IAAS_EC2ARN} --SSMKMSKeyForPiiArnName cum_kms_key_IaaSEaiForPii --SSMKMSKeyForPhiArnName cum_kms_key_IaaSEaiForPhi --logLevel INFO
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


# Startup code excution from here
if __name__ == '__main__':

	
    parser = ArgumentParser()

    parser.add_argument("--stackName", dest="stackName", required=True, metavar="<stackName>",
                        help="Cloud Formation Stack Name")
    parser.add_argument("--templateUrl", dest="templateUrl", required=True, metavar="<templateUrl>",
                        help="Cloud Formation Template S3 Path")
    parser.add_argument("--UserArn", dest="UserArn", required=True, metavar="<UserArn>",
                        help="UserArn Identifier value")
    parser.add_argument("--IAASEC2Arn", dest="IAASEC2Arn", required=True, metavar="<IAASEC2Arn>",
                        help="IAASEC2Arn Identifier value")
    parser.add_argument("--SSMKMSKeyForPiiArnName", dest="SSMKMSKeyForPiiArnName", required=True, metavar="<SSMKMSKeyForPiiArnName>",
                        help="SSM Key KMS ARN for Pii")
    parser.add_argument("--SSMKMSKeyForPhiArnName", dest="SSMKMSKeyForPhiArnName", required=True, metavar="<SSMKMSKeyForPhiArnName>",
                        help="SSM Key KMS ARN for Phi")
 
    parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<LogLevel>",
                       help="Logging level INFO|DEBUG|ERROR|WARNING")

    args = parser.parse_args()
    try:       

        logLevel = args.logLevel
        if logLevel is None:
            logLevel = 'INFO'

        input_params = dict()

        input_params['stackName'] = args.stackName
        input_params['templateUrl'] = args.templateUrl
        input_params['UserArn'] = args.UserArn
        input_params['IAASEC2Arn'] = args.IAASEC2Arn
        input_params['SSMKMSKeyForPiiArnName'] = args.SSMKMSKeyForPiiArnName
        input_params['SSMKMSKeyForPhiArnName'] = args.SSMKMSKeyForPhiArnName
        

        baseDir = os.getcwd()
        logDir = baseDir + "/log"
        if not os.path.exists(logDir):
            os.makedirs(logDir)

        logFile = logDir +  '/'+os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'
        logging.basicConfig(filename=logFile, filemode='w', level=logLevel, format='%(asctime)s   %(levelname)s     %(message)s')

        logging.info("Input parameter details are as below:") 
        logging.info(input_params)

        logging.debug("**************************************************")
        logging.debug("Triggring AWS stack creation for $1 ...")
        logging.debug("**************************************************")

        cloudformation = boto3.resource('cloudformation')

        cloudformation.create_stack(StackName=input_params['stackName'],\
                                    TemplateURL=input_params['templateUrl'],\
                                    Parameters=[{'ParameterKey':'UserArn','ParameterValue':input_params['UserArn']},
                                                {'ParameterKey':'IAASEC2Arn','ParameterValue':input_params['IAASEC2Arn']},
                                                {'ParameterKey':'SSMKMSKeyForPiiArnName','ParameterValue':input_params['SSMKMSKeyForPiiArnName']},
                                                {'ParameterKey':'SSMKMSKeyForPhiArnName','ParameterValue':input_params['SSMKMSKeyForPhiArnName']}]
                                    )
        
        common_modules.get_stack_status(cloudformation, input_params['stackName'])




    except Exception as exp:
        logging.error("Caught Exception %s", str(exp))
        traceback.print_exc(file=sys.stdout)
        logging.error('exiting ....')
        raise OSError("Caught Exception %s", str(exp))
        sys.exit(-1)
