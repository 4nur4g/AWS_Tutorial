# References
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.list_inventory_entries
# https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-inventory-schema.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html
'''
In this file we are fetching details from online SSM EC2 instances
who are running for less than 30 minutes and storing
their details in S3 bucket.
Guidelines:
    1: Instances have SSM Agents Installed.
    2: Instances have AmazonSSMManagedInstanceCore policy.
    3: If you are using lambda function to call the instance
       following policy should be attached
       1: AmazonS3FullAccess (If Lambda funcation is storing files to bucket)
       2: AmazonEC2ReadOnlyAccess.
       3: AmazonSSMFullAccess.
       4: AWSLambdaExecute  
'''
import json
import boto3
import time
from datetime import datetime

def lambda_handler(event, context):
    # boto3 client
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')
    s3 = boto3.resource('s3')
    
    # getting instance information and ssm instance information
    describeInstance = ec2.describe_instances()
    ssm_describeInstance = ssm.describe_instance_information()
    
    '''
    In this loop we are creating a list of those
    instance id's which are running for less then
    30 minutes even if SSM is enable or not 
    '''
    instanceId = []
    for i in describeInstance['Reservations']:
        for instance in i['Instances']:
            # only getting those instance which are running
            if instance["State"]["Name"] == "running":
                time = instance['LaunchTime']
                diff_seconds = int(float(datetime.now().timestamp())) - int(float(time.timestamp()))
                # checking running time of instance is less then 30 minutes
                # then only append those instance id's in instanceId list
                if diff_seconds < 1800:
                    instanceId.append(instance['InstanceId'])
    # print(instanceId)
    
    '''
    In this loop we are fetching online SSM enable
    instances id's and checking if i['InstanceId]
    is present in instanceId.
    Why we have to do this because i am not able to find instance
    launch time in SSM describe_instance_information()
    '''
    for i in ssm_describeInstance['InstanceInformationList']:
        # checking those instance id's which are present in
        #instanceId list
        if i['InstanceId'] in instanceId:
            final_dict = {}
            final_dict['InstanceId'] = i['InstanceId']
            final_dict['PingStatus'] = i['PingStatus']
            final_dict['PlatformName'] = i['PlatformName']
            final_dict['PlatformType'] = i['PlatformType']
            final_dict['IPAddress'] = i['IPAddress']
            
    # dump json object to bucket
    bucket_name = 'your-bucket-name'
    filename = 'your-json-filename.json'
    s3object = s3.Object(bucket_name, filename)
    s3object.put(
        Body=(bytes(json.dumps(final_dict).encode('UTF-8')))
        )
    return final_dict
