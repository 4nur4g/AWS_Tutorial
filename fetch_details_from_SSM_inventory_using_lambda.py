# References
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.list_inventory_entries
# https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-inventory-schema.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html

import json
import boto3
import time
from datetime import datetime

def lambda_handler(event, context):
    # boto3 client
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')
    s3 = boto3.resource('s3')
    
    # getting instance information
    describeInstance = ec2.describe_instances()
    # gettings ssm instance information
    ssm_describeInstance = ssm.describe_instance_information()

    '''
    In this loop we are creating a list of those
    instance id's which are running for less then
    30 minutes even if SSM is enable or not 
    '''
    instanceId = []
    final_dict = {}
    final_list = []
    for i in describeInstance['Reservations']:
        for instance in i['Instances']:
            if instance["State"]["Name"] == "running":
                time = instance['LaunchTime']
                diff_seconds = int(float(datetime.now().timestamp())) - int(float(time.timestamp())) 
                if diff_seconds < 1800:
                    instanceId.append(instance['InstanceId'])
    
    '''
    In this loop we are fetching online SSM enable
    instances id's and checking if i['InstanceId]
    is present in instanceId
    '''

    for i in ssm_describeInstance['InstanceInformationList']:
        if i['InstanceId'] in instanceId:
            final_dict['InstanceId'] = i['InstanceId']
            final_dict['PingStatus'] = i['PingStatus']
            final_dict['PlatformName'] = i['PlatformName']
            final_dict['PlatformType'] = i['PlatformType']
            final_dict['IPAddress'] = i['IPAddress']
            
            # getting inventory details Applications installed
            inventory = ssm.list_inventory_entries(
                InstanceId=i['InstanceId'],
                TypeName='AWS:Application'
                )
            final_dict['Applications'] = inventory['Entries']
            final_list.append(final_dict.copy())
                
        else:
            return {'response': 'there are no ssm instance within 30 min launch time'}
    
    # dump json object to bucket
    bucket_name = 'paradoxtestingbucket'
    filename = 'demo.json'
    s3object = s3.Object(bucket_name, filename)
    s3object.put(
        Body=(bytes(json.dumps(final_list).encode('UTF-8')))
        )
    return final_list
