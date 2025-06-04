
'''
Copyright (C) 2019 Medtronic Diabetes.
All Rights Reserved.
This software is the confidential and proprietary information of
Medtronic Diabetes.  Confidential Information.  You shall not
disclose such Confidential Information and shall use it only in
accordance with the terms of the license agreement you entered into
with Medtronic Diabetes.
Cum-CP-SignKey
For Cum-BLE-SignKey
python3 -W ignore core/scripts/deploySignKMSkey.py --UserArn  arn:aws:iam::812470574530:user/CumulusDev-AWScli-ProgAccess --aliasName alias/Cum-BLE-SignKey --KMSKeyArnSSMdata ble_signkey_Data_arn --KMSKeyArnSSMSSE ble_signkey_arn_SSE --logLevel INFO

For Cum-CP-SignKey
python3 -W ignore core/scripts/deploySignKMSkey.py --UserArn  arn:aws:iam::812470574530:user/CumulusDev-AWScli-ProgAccess --aliasName alias/Cum-CP-SignKey --KMSKeyArnSSMdata cp_signkey_Data_arn --KMSKeyArnSSMSSE cp_signkey_arn_SSE --logLevel INFO

For Fota-SignKey
python3 -W ignore core/scripts/deploySignKMSkey.py --UserArn  arn:aws:iam::384332682840:user/cumulus-awscli-pa --aliasName alias/Fota-SignKey --KMSKeyArnSSMdata fota_signkey_Data_arn --KMSKeyArnSSMSSE fota_signkey_arn_SSE --logLevel INFO

For Janus-Synergy-SignKey
python3 -W ignore core/scripts/deploySignKMSkey.py --UserArn  arn:aws:iam::317893085106:user/CumulusStage-AWScli-ProgAccess --aliasName alias/Janus-Synergy-SignKey --KMSKeyArnSSMdata janus_synergy_arn --KMSKeyArnSSMSSE janus_synergy_arn_SSE --logLevel INFO

python3 -W ignore core/scripts/deploySignKMSkey.py --UserArn  arn:aws:iam::424069389173:user/CumulusFalcon-AWScli-ProgAccess --aliasName alias/CP-kms-key --KMSKeyArnSSMdata CP_kms_key_arn --KMSKeyArnSSMSSE CP_kms_key_SSE --logLevel INFO
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
import boto3

KeyInfo = dict()
client = boto3.client('kms')


def args_parse():
    parser = ArgumentParser()

    parser.add_argument("--UserArn", dest="UserArn", required=True, metavar="<UserArn>",
                        help="CLI User Arn")
    parser.add_argument("--aliasName", dest="aliasName", required=True, metavar="<aliasName>",
                        help="CLI User Arn")
    parser.add_argument("--KMSKeyArnSSMdata", dest="KMSKeyArnSSMdata", required=True, metavar="<KMSKeyArnSSMdata>",
                        help="CLI User Arn")
    parser.add_argument("--KMSKeyArnSSMSSE", dest="KMSKeyArnSSMSSE", required=True, metavar="<KMSKeyArnSSMSSE>",
                        help="CLI User Arn")
    parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<LogLevel>",
                        help="Logging level INFO|DEBUG|ERROR|WARNING")
    args = parser.parse_args()
    return args


def deploy_KMS_Key(UserArn):
    try:
        baseDir = os.getcwd()
        logLevel = args.logLevel
        logDir = baseDir + "/log"
        if logLevel is None:
            logLevel = 'INFO'

        if not os.path.exists(logDir):
            os.makedirs(logDir)
            logFile = logDir + '/' + os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M",
                                                                                                gmtime()) + '.log'
            logging.basicConfig(filename=logFile, filemode='w', level=logLevel,
                                format='%(asctime)s %(levelname)s  %(message)s')
            print('Log File Location : ' + os.path.abspath(logFile))
        AccountId = UserArn.split(':')[4]
        response = client.create_key(
            Policy='''{
						"Id": "key-consolepolicy-3",
					    "Version": "2012-10-17",
					    "Statement": [
					        {
					            "Sid": "Enable IAM User Permissions",
					            "Effect": "Allow",
					            "Principal": {
					                "AWS": "arn:aws:iam::'''+AccountId+''':root"
					            },
					            "Action": "kms:*",
					            "Resource": "*"
					        },
					        {
					            "Sid": "Allow access for Key Administrators",
					            "Effect": "Allow",
					            "Principal": {
					                "AWS": [
					                    "arn:aws:iam::'''+AccountId+''':role/CumulusAdminRW",
					                    "'''+args.UserArn+'''"
					                ]
					            },
					            "Action": [
					                "kms:Create*",
					                "kms:Describe*",
					                "kms:Enable*",
					                "kms:List*",
					                "kms:Put*",
					                "kms:Update*",
					                "kms:Revoke*",
					                "kms:Disable*",
					                "kms:Get*",
					                "kms:Delete*",
					                "kms:TagResource",
					                "kms:UntagResource"
					            ],
					            "Resource": "*"
					        },
					        {
					            "Sid": "Allow use of the key",
					            "Effect": "Allow",
					            "Principal": {
					                "AWS": [
					                    "arn:aws:iam::'''+AccountId+''':role/CumLambdaAccessRole",
					                    "'''+args.UserArn+'''"
					                ]
					            },
					            "Action": [
					                "kms:DescribeKey",
					                "kms:GetPublicKey",
					                "kms:Sign",
					                "kms:Verify"
					            ],
					            "Resource": "*"
					        },
					        {
					            "Sid": "Allow attachment of persistent resources",
					            "Effect": "Allow",
					            "Principal": {
					                "AWS": [
					                    "arn:aws:iam::'''+AccountId+''':role/CumLambdaAccessRole",
					                    "'''+args.UserArn+'''"
					                ]
					            },
					            "Action": [
					                "kms:CreateGrant",
					                "kms:ListGrants",
					                "kms:RevokeGrant"
					            ],
					            "Resource": "*",
					            "Condition": {
					                "Bool": {
					                    "kms:GrantIsForAWSResource": "true"
					                }
					            }
					        }
					    ]
					}''',
            Description='KMS Key required for generating signature via KMS keys',
            KeyUsage='SIGN_VERIFY',
            CustomerMasterKeySpec='RSA_2048',
            Origin='AWS_KMS',
            BypassPolicyLockoutSafetyCheck=False,
        )

        logging.info("KMS Key is Created")
        print("KMS Key is Created successfully")

        KeyInfo['Arn'] = response['KeyMetadata']['Arn']
        KeyInfo['Keyid'] = response['KeyMetadata']['KeyId']
        return KeyInfo

    except Exception as exp:
        logging.error("Caught Exception %s", str(exp))
        traceback.print_exc(file=sys.stdout)
        logging.error('exiting ....')
        raise OSError("Caught Exception %s", str(exp))


def Create_alias(aliasName, Keyid):
    try:
        print("Creating Alias for KMS Key.")
        logging.info("Creating Alias for KMS Key.")

        response = client.create_alias(
            AliasName=aliasName,
            TargetKeyId=Keyid
        )

        print("Alias is created with: " +aliasName)
    except Exception as exp:
        logging.error("Caught Exception %s", str(exp))
        print("Caught Exception %s", str(exp))
        # Keyid = response['KeyMetadata']['KeyId']


if __name__ == '__main__':

    args = args_parse()
    logLevel = args.logLevel
    if args.logLevel is None:
        logLevel = 'INFO'
    baseDir = os.getcwd()
    logDir = baseDir + "/log"
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    logFile = logDir + '/' + os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'
    logging.basicConfig(filename=logFile, filemode='w', level=args.logLevel,
                        format='%(asctime)s   %(levelname)s     %(message)s')
    print('Log File Location : ' + os.path.abspath(logFile))

    try:

        KeyInfo = deploy_KMS_Key(args.UserArn, )
        time.sleep(5)
        logging.info("Created KMS Key.")
        print("KMS Key is Created successfully.")
        print("KMS Key is Created with Key ARN: " + KeyInfo['Arn'])

        Create_alias(args.aliasName, KeyInfo['Keyid'])
        logging.info("Alias is created")
        print("Alias is created for the KMS key successfully")
        print('Log File Location : ' + os.path.abspath(logFile))

        ssm = boto3.client('ssm')
        response = ssm.put_parameter(Name=args.KMSKeyArnSSMdata,
                                     Description='Data SSM Parameter for KMS Key ARN',
                                     Value=KeyInfo['Arn'], Type='String', Overwrite=True)
        response = ssm.put_parameter(Name=args.KMSKeyArnSSMSSE,
                                     Description='SSE SSM Parameter for KMS Key ARN',
                                     Value=KeyInfo['Arn'], Type='String', Overwrite=True)
    except Exception as exp:
        logging.error("Caught Exception %s", str(exp))
        print("Caught Exception %s", str(exp))
        print('Log File Location : ' + os.path.abspath(logFile))