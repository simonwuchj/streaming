import json
import os
import boto3
import logging
import uuid
import random
from urllib.parse import urlparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.resource('s3')

def get_mediaconvert_jobs(bucket):
	jobs, jobInput = list(), dict()
	# Iterates through all the objects in jobs folder of the WatchFolder bucket, doing the pagination for you. Each obj
	# contains a jobSettings JSON
	for obj in bucket.objects.filter(Prefix='jobs/'):
		if obj.key != "jobs/":
			jobInput['filename'] = obj.key
			logger.info('jobInput: %s', jobInput['filename'])

			jobInput['settings'] = json.loads(obj.get()['Body'].read())
			logger.info(json.dumps(jobInput['settings'])) 
				
			jobs.append(jobInput)
		
	# Use Default job settings in the lambda zip file in the current working directory
	if not jobs:
			
		with open('job.json') as json_data:
			jobInput['filename'] = 'Default'
			logger.info('jobInput: %s', jobInput['filename'])

			jobInput['settings'] = json.load(json_data)
			logger.info(json.dumps(jobInput['settings']))
			
			jobs.append(jobInput)

	return jobs

def assign_dst_val(outputGroup, grpsetting, sourceS3Key, fileName):
	destinationS3 = 's3://' + os.environ['DestinationBucket'] + '/' \
				+ os.path.splitext(os.path.basename(sourceS3Key))[0] + '/' \
				+ os.path.splitext(os.path.basename(fileName))[0] 
	templateDestination = outputGroup['OutputGroupSettings'][grpsetting]['Destination']
	templateDestinationKey = urlparse(templateDestination).path
	logger.info("templateDestinationKey == %s", templateDestinationKey)
	outputGroup['OutputGroupSettings'][grpsetting]['Destination'] = destinationS3+templateDestinationKey

def updatejobfromS3Evt(job, sourceS3Key):
	for outputGroup in job['settings']['OutputGroups']:
		if outputGroup['OutputGroupSettings']['Type'] == 'FILE_GROUP_SETTINGS':
			assign_dst_val(outputGroup, 'FileGroupSettings', sourceS3Key, job['filename'])

		elif outputGroup['OutputGroupSettings']['Type'] == 'HLS_GROUP_SETTINGS':
			assign_dst_val(outputGroup, 'HlsGroupSettings', sourceS3Key, job['filename'])

		elif outputGroup['OutputGroupSettings']['Type'] == 'DASH_ISO_GROUP_SETTINGS': 
			assign_dst_val(outputGroup, 'DashIsoGroupSettings', sourceS3Key, job['filename'])

		elif outputGroup['OutputGroupSettings']['Type'] == 'MS_SMOOTH_GROUP_SETTINGS':
			assign_dst_val(outputGroup, 'MsSmoothGroupSettings', sourceS3Key, job['filename'])

		else:
			logger.error("Exception: Unknown Output Group Type %s", outputGroup['OutputGroupSettings']['Type'])
			raise

def lambda_handler(event, context):
	assetID = str(uuid.uuid4())
	statusCode = 200
	destinationS3 = 's3://' + os.environ['DestinationBucket']
	mediaConvertRole = os.environ['MediaConvertRole']
	region = os.environ['AWS_DEFAULT_REGION']
	mclient = boto3.client('mediaconvert', region_name=region)
	endpoints = mclient.describe_endpoints()
	# add the account-specific endpoint to the client session 
	mediaConvertClient = boto3.client('mediaconvert', region_name=region, endpoint_url=endpoints['Endpoints'][0]['Url'], verify=False)

	for record in event['Records']:
		try:
			sourceS3Bucket = record['s3']['bucket']['name']
			sourceS3Key = record['s3']['object']['key']
			sourceS3 = 's3://'+ sourceS3Bucket + '/' + sourceS3Key
			bucket = s3.Bucket(sourceS3Bucket)
			jobMetadata = {
				'assetID': assetID, 
				'application': os.environ['Application'],
				'input': sourceS3
			}

			# get related data from json template
			jobs = get_mediaconvert_jobs(bucket)

			# uplate json template with s3 event
			for job in jobs:
				jobMetadata['settings'] = job['filename']
				job['settings']['Inputs'][0]['FileInput'] = sourceS3

				updatejobfromS3Evt(job, sourceS3Key)

				logger.info(json.dumps(job['settings']))
				job = mediaConvertClient.create_job(Role=mediaConvertRole, UserMetadata=jobMetadata, Settings=job['settings'])

		except Exception as e:
			logger.error('Exception: %s', e)
			statusCode = 500
			raise

	return {
		'statusCode': statusCode,
		'body': json.dumps(job, indent=4, sort_keys=True, default=str),
		'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
	}

