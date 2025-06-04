
import argparse
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

	parser = argparse.ArgumentParser()
	parser.add_argument('--stackName', type=str, required=True)
	parser.add_argument('--templateurl', type=str, required=True)
	parser.add_argument("--logLevel", dest="logLevel", required=False, metavar="<LogLevel>",
	                   help="Logging level INFO|DEBUG|ERROR|WARNING")
	args = parser.parse_args()
	try:
		logDir = os.getcwd() + "/log"
		if not os.path.exists(logDir):
		    os.makedirs(logDir)
		logFile = logDir +  '/'+os.path.splitext(os.path.basename(__file__))[0] + strftime("%Y%m%d%H%M", gmtime()) + '.log'
		logging.basicConfig(filename=logFile, filemode='w', level=args.logLevel, format='%(asctime)s   %(levelname)s     %(message)s')


		cloudformation = boto3.resource('cloudformation')

		logging.debug("**************************************************")
		logging.debug("Triggring AWS stack creation for $1 ...")
		logging.debug("**************************************************")

		response = cloudformation.create_stack(
			StackName = args.stackName,
			TemplateURL = args.templateurl,
			Capabilities=['CAPABILITY_IAM']
		)
		common_modules.get_stack_status(cloudformation, args.stackName)
	except Exception as exp:
		logging.error("Caught Exception %s", str(exp))
		traceback.print_exc(file=sys.stdout)
		logging.error('exiting ....')
		raise OSError("Caught Exception %s", str(exp))
		sys.exit(-1)   
