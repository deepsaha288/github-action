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
import subprocess
from netaddr import IPNetwork


# Generic used everywhere - Function to get stack status
def get_stack_status(cloudformation, stack_name):
    ret = 0
    logging.info( "Checking for status of stack: %s", stack_name)

    while True:
        stack = cloudformation.Stack(stack_name)
        #print stack
        if (stack.stack_status.find("CREATE_COMPLETE") != -1) :
            logging.info( "Stack creation completed...")
            print("Stack creation completed...")
            ret = 0
            break
        elif (stack.stack_status.find("CREATE_IN_PROGRESS") != -1) :
            logging.info( "Stack creation is in progress ... ")
            print("Stack creation is in progress ... ")
            time.sleep(10)
        # added below elif conditions for update stack status check
        elif (stack.stack_status.find("UPDATE_IN_PROGRESS") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
        elif (stack.stack_status.find("UPDATE_COMPLETE") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
            break
        elif (stack.stack_status.find("DELETE_IN_PROGRESS") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
        elif (stack.stack_status.find("DELETE_COMPLETE") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)    	
        elif (stack.stack_status.find("UPDATE_COMPLETE_CLEANUP_IN_PROGRESS") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
        # added above elif conditions for update stack status check
        else:
            #print stack.stack_status
            logging.error( "Stack creation failed with below status: %s", stack.stack_status)
            print("Stack creation failed with below status: %s", stack.stack_status)
            ret  = 1
            raise OSError("Stack creation failed RollBack in progress.")
            break
    
    return ret

# Create - Function to get stack status of new stack getting created
def get_create_stack_status(cloudformation, stack_name):
    ret = 0
    logging.info( "Checking for status of stack: %s", stack_name)

    while True:
        stack = cloudformation.Stack(stack_name)
        #print stack
        if (stack.stack_status.find("CREATE_COMPLETE") != -1) :
            logging.info( "Stack creation completed...")
            print("Stack creation completed...")
            ret = 0
            break
        elif (stack.stack_status.find("CREATE_IN_PROGRESS") != -1) :
            logging.info( "Stack creation is in progress ... ")
            print("Stack creation is in progress ... ")
            time.sleep(10)
        else:
            #print stack.stack_status
            logging.error( "Stack creation failed with below status: %s", stack.stack_status)
            print("Stack creation failed with below status: %s", stack.stack_status)
            ret  = 1
            raise OSError("Stack creation failed RollBack in progress.")
            break
    
    return ret


# Update - Function to get stack status of existing stack getting updated
def get_update_stack_status(cloudformation, stack_name):
    
    ret = 0
    logging.info( "Checking for status of stack: %s", stack_name)

    while True:
        stack = cloudformation.Stack(stack_name)
        #print stack
        if (stack.stack_status.find("CREATE_COMPLETE") != -1) :
            logging.info( "Stack creation completed...")
            print("Stack creation completed...")
            ret = 0
            break
        elif (stack.stack_status.find("CREATE_IN_PROGRESS") != -1) :
            logging.info( "Stack creation is in progress ... ")
            print("Stack creation is in progress ... ")
            time.sleep(10)
        elif (stack.stack_status.find("UPDATE_IN_PROGRESS") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
        elif (stack.stack_status.find("UPDATE_COMPLETE") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
            break
        elif (stack.stack_status.find("DELETE_IN_PROGRESS") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
        elif (stack.stack_status.find("DELETE_COMPLETE") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)    	
        elif (stack.stack_status.find("UPDATE_COMPLETE_CLEANUP_IN_PROGRESS") != -1) :
            logging.info( "Stack update is in progress ... ")
            print("Stack update is in progress ... ")
            time.sleep(10)
        else:
            #print stack.stack_status
            logging.error( "Stack creation failed with below status: %s", stack.stack_status)
            print("Stack creation failed with below status: %s", stack.stack_status)
            ret  = 1
            raise OSError("Stack creation failed RollBack in progress.")
            break
    
    return ret

def get_delete_stack_status(cloudformation, stack_name): 
    ret = 0
    logging.info( "Checking for status of stack: %s", stack_name)

    while True:
        response = cloudformation.describe_stacks(StackName=stack_name)
        if ((response['Stacks'][0]['StackName']) == stack_name):
            logging.info( "Stack deletion is in progress ... ")
            print("Stack deletion in progress...")
            time.sleep(10)
        elif ((response['Stacks'][0]['StackName']) != stack_name):
            logging.info( "Stack deletion is completed...")
            print("Stack deletion is completed.")
            ret = 0
            break
        else:
            print("Stack deletion failed...")
            ret = 1
            raise OSError("Stack creation failed RollBack in progress.")
            break

    return ret

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

def get_bucket_file_list(s3, bucketName):
    fileList = []
    bucketObjList = s3.list_objects(Bucket=bucketName)
    if 'Contents' in bucketObjList:
        for bucketObj in bucketObjList['Contents']:
            fileList.append(bucketObj['Key'])
    return fileList

def compile(input_params): 
     os.chdir(input_params['appPath'])

     if input_params['buildType'].lower() == "zip":
        cmd = 'gradle clean build fatZip'
     else:
        cmd = 'gradle clean buildJar copyBuilds'

     proc = subprocess.call(cmd, shell=True)
     if proc == 0:
         logging.info("Build successful...")
     else:
         logging.info("Build failed...")


def getAvailableIPList(subnetID,count,ignore_ips): 
    ec2 = boto3.resource('ec2')
    cidr=ec2.Subnet(subnetID).cidr_block
    client=boto3.client('ec2')
    response = client.describe_network_interfaces()
    content = response['NetworkInterfaces']
    used_ips=[]
    available_ips=[]
    counter=0
    for i in range(len(content)):
        used_ips.append(content[i]['PrivateIpAddress'])
    for ip in IPNetwork(cidr)[4:]:
        if str(ip) not in used_ips and counter<count and str(ip) not in ignore_ips and str(ip).split('.')[3]!='255':
            available_ips.append(str(ip))
            counter+=1
    return available_ips


def deleteENI(ec2,ec2_client,ips):
    response = ec2_client.describe_network_interfaces()
    logging.info(response)

    ips_list = list()

    if type(ips) == str:
        ips_list.append(ips)
    elif type(ips) == list:
        ips_list = ips

    iserror=0
    content = response['NetworkInterfaces']

    for ip in ips_list:
        flag = 0
        print("\nProcessing IP " + ip)
        logging.info("\nProcessing IP " + ip)
        for i in range(len(content)):
            if content[i]['PrivateIpAddress'] == ip:
                if content[i]['Status'] == 'in-use':
                    flag = 1
                    print("ERROR: Private IP Address is in-use")
                    logging.error("ERROR: Private IP Address is in-use")
                    iserror=1
                    break
                else:
                    network_interface = ec2.NetworkInterface(content[i]['NetworkInterfaceId'])
                    network_interface.delete()
                    flag = 1
                    print("ENI for " + ip + " deleted")
                    logging.info("ENI for " + ip + " deleted")
                    break
        if flag == 0:
            print("IP " + ip + " not attached to any ENI. Safe to use")
            logging.info("IP " + ip + " not attached to any ENI. Safe to use")
    if iserror == 1 :
        raise OSError ("Error")
        sys.exit(-1)
