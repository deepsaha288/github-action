'''
Copyright (C) 2019 Medtronic Diabetes.
All Rights Reserved.
This software is the confidential and proprietary information of
Medtronic Diabetes.  Confidential Information.  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Medtronic Diabetes.
'''
import boto3
import traceback
from argparse import ArgumentParser
import os
import sys
import logging
from time import sleep, gmtime, strftime
import time
import yaml
sys.path.append('common_modules/')
sys.path.append('../common_modules/')
sys.path.append('../../common_modules/')
import common_modules

if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument("--stackName", dest="stackName", required=True, metavar="<stackName>",
                        help="Cloud Formation Stack Name for KMS Key Creation")
    parser.add_argument("--templateUrl", dest="templateUrl", required=True, metavar="<templateUrl>",
                        help="Cloud Formation Template S3 Path")
    parser.add_argument("--configFilePath", dest="configFilePath", required=True, metavar="<configFilePath>",
                        help="Config file path")
    parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<logLevel>",default="INFO",
                       help="Logging level INFO|DEBUG|ERROR|WARNING")
    args = parser.parse_args()
    
    logDir = os.getcwd() + "/log"
    if not os.path.exists(logDir):
        os.makedirs(logDir)
        
    templateDir=os.getcwd() + "/temp"
    if not os.path.exists(templateDir):
        os.makedirs(templateDir)
    else:
        for fname in os.listdir(os.getcwd() + "/temp"):
            os.remove(os.getcwd() + "/temp/"+fname)
            
    try: 
        
        logFile = logDir +  '/'+os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'
        logging.basicConfig(filename=logFile, filemode='w', level=args.logLevel, format='%(asctime)s   %(levelname)s     %(message)s')
        

        logging.info("Reading Config File.")
        s3 = boto3.client('s3')
        
        with open(args.configFilePath) as config_file:  
            data = yaml.load(config_file)
            
            input_params = dict()
            input_params['idpProvider'] = data['IDPProvider']
            input_params['roleName'] = data['RoleName']
            input_params['stsRoleSSMKeyName'] = data['STSRoleSSMKeyName']

            rulestr = list()
            for value in data['Audiences']:
                rulestr.append(value)
            rulestr = (','.join(rulestr))
            input_params['rulestr'] = str(rulestr)[1:-1]

        cloudformation = boto3.resource('cloudformation')

       
        cloudformation.create_stack(
                                    StackName=args.stackName,
                                    TemplateURL=args.templateUrl,
                                    Capabilities=['CAPABILITY_NAMED_IAM'],
                                    Parameters=[
                                        {'ParameterKey':'IDPProvider','ParameterValue':input_params['idpProvider']},
                                        {'ParameterKey':'RuleString','ParameterValue':input_params['rulestr']},
                                        {'ParameterKey':'RoleName','ParameterValue':input_params['roleName']},
                                        {'ParameterKey':'STSRoleSSMKeyName','ParameterValue':input_params['stsRoleSSMKeyName']}
                                    ]
                                )
        common_modules.get_stack_status(cloudformation, args.stackName)
        
        print( "Stack "+args.stackName+" deployed successfully...")
        logging.info("\nStack "+args.stackName+" deployed successfully...")

        # deleting temporary files        
        for fname in os.listdir(os.getcwd() + "/temp"):
            os.remove(os.getcwd() + "/temp/"+fname)
        os.rmdir(os.getcwd() + "/temp")
                    
    except Exception as exp:
        logging.error("Caught Exception %s", str(exp))
        print("Error occured.")
        traceback.print_exc()
        raise OSError("Caught Exception %s", str(exp))    
        sys.exit()
