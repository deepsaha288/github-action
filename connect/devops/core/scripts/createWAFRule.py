'''
Copyright (C) 2019 Medtronic Diabetes.
All Rights Reserved.
This software is the confidential and proprietary information of
Medtronic Diabetes.  Confidential Information.  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Medtronic Diabetes.
'''
'''
python3 -W ignore core/scripts/createWAFRule.py --name cum-waf-rule-apigw-lgen --metricName "webACLforAPIGW" --ssmWAFparameterName WebAclIdAPIGW --logLevel INFO
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
def create_WAF(args) :
    input_params= dict()
    input_params['name']=args.name
    input_params['metricName']=args.metricName
    input_params['ssmWAFparameterName']=args.ssmWAFparameterName

    client = boto3.client('waf-regional')
    token_obj= client.get_change_token()
    token=str(token_obj['ChangeToken'])

    res=client.list_web_acls()
    for acl in res['WebACLs']: 
        if acl['Name']==args.name:
            print('Web ACL already exists with the same name')
            logging.info("Web ACL already exists with the same name")
            return

    try:
        response = client.create_web_acl(
            Name=input_params['name'],
            MetricName=input_params['metricName'],
            DefaultAction={
                'Type': 'ALLOW'
            },
            ChangeToken=str(token)
        )
        print(response)
        print(response['WebACL']['WebACLId'])
        WebAclId=str(response['WebACL']['WebACLId'])
    except Exception as e:
        print(e)
        logging.error(e) 
        traceback.print_exc()
    
    print("WAF creation successful")
    logging.info("WAF creation successful")

    try:
        cl=boto3.client('ssm')
        response=cl.put_parameter(
        Name=input_params['ssmWAFparameterName'],
        Description='Web ACL Id',
        Value=WebAclId,
        Type='String',
        Overwrite=True)

    except Exception as e:
        print(e)
        logging.error(e)
        traceback.print_exc()
        raise OSError(e)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--name", dest="name", required=True, metavar="<name>",
                        help="Name of the WebACL created")
    parser.add_argument("--metricName", dest="metricName", required=True, metavar="<metricName>",
                        help="Name for the CloudWatch metric")
    parser.add_argument("--ssmWAFparameterName", dest="ssmWAFparameterName", required=True, metavar="<ssmWAFparameterName>")
    parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<logLevel>",default="INFO",
                       help="Logging level INFO|DEBUG|ERROR|WARNING")
    args = parser.parse_args()
    logDir = os.getcwd() + "/log"
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    logFile = logDir +  '/'+os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'
    logging.basicConfig(filename=logFile, filemode='w', level=args.logLevel, format='%(asctime)s   %(levelname)s     %(message)s')
    val=create_WAF(args) 
