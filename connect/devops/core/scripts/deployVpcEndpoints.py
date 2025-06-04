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


# Startup code excution from here
if __name__ == '__main__':

	
    parser = ArgumentParser()

    parser.add_argument("--stackName", dest="stackName", required=True, metavar="<stackName>",
                        help="Cloud Formation Stack Name")
    parser.add_argument("--templateUrl", dest="templateUrl", required=True, metavar="<templateUrl>",
                        help="Cloud Formation Template S3 Path")
    parser.add_argument("--vpcId", dest="vpcId", required=True, metavar="<vpcId>",
                        help="Vpc Identifier value")
    parser.add_argument("--subnetIds", dest="subnetIds", required=True, metavar="<subnetIds>",
                        help="subnetIds Identifier value")
    parser.add_argument("--ssmKeySTSEndpoint", dest="SSMKeySTSEndpoint", required=True, metavar="<SSMKeySTSEndpoint>",
                        help="SSM Key to store STS Endpoint URL")
    parser.add_argument("--AWSRegion", dest="region", required=True, metavar="<AWSRegion>",
                        help="AWS Region")  
    parser.add_argument("--routeTableIds", dest="routeTableIds", required=True, metavar="<routeTableIds>",
                        help="routeTableIds Identifier value")
    parser.add_argument("--privateDnsEnabled", dest="PrivateDnsEnabled", required=True, metavar="<PrivateDnsEnabled>",
                        help="PrivateDnsEnabled value true/false")


 
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
        input_params['vpcId'] = args.vpcId
        input_params['subnetIds'] = args.subnetIds
        input_params['routeTableIds'] = args.routeTableIds
        input_params['PrivateDnsEnabled'] = args.PrivateDnsEnabled
        input_params['SSMKeySTSEndpoint'] = args.SSMKeySTSEndpoint
        input_params['AWSregion'] = args.region

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
                                    Parameters=
                                      [
                                        {'ParameterKey':'VpcId','ParameterValue':input_params['vpcId']},
                                        {'ParameterKey':'SubnetIds','ParameterValue':input_params['subnetIds']},
                                        {'ParameterKey':'PrivateDnsEnabled','ParameterValue':input_params['PrivateDnsEnabled']},
                                        {'ParameterKey':'RouteTableIds','ParameterValue':input_params['routeTableIds']},
                                        {'ParameterKey':'SSMKeySTSEndpoint','ParameterValue':input_params['SSMKeySTSEndpoint']},
                                        {'ParameterKey':'AWSRegion','ParameterValue':input_params['AWSregion']}
                                      ]
                                    )
        
        common_modules.get_stack_status(cloudformation, input_params['stackName'])

    except Exception as exp:
        logging.error("Caught Exception %s", str(exp))
        traceback.print_exc(file=sys.stdout)
        logging.error('exiting ....') 
        raise OSError("Caught Exception %s", str(exp))   
        sys.exit(-1)   
