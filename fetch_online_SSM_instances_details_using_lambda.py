'''
References:
    1: OS Instances names which have SSM Agent preinstalled
        -> https://docs.aws.amazon.com/systems-manager/latest/userguide/prereqs-ssm-agent.html
    2: If you want to extract more details of any SSM Instances
        -> https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.list_inventory_entries
'''
import json
import boto3

def lambda_handler(event, context):
    # boto3 client
    ssm = boto3.client('ssm')
    s3 = boto3.resource('s3')
    
    # getting ssm instance information
    ssm_describeInstance = ssm.describe_instance_information()
    
    '''
    In this loop we are fetching online SSM enable
    instances details
    '''
    final_list = []
    for i in ssm_describeInstance['InstanceInformationList']:
        details_dict = {}
        details_dict['InstanceId'] = i['InstanceId']
        details_dict['PingStatus'] = i['PingStatus']
        details_dict['PlatformName'] = i['PlatformName']
        details_dict['PlatformType'] = i['PlatformType']
        details_dict['IPAddress'] = i['IPAddress']
        final_list.append(details_dict)
            
    # dump json object to bucket
    # bucket_name = 'your-bucket-name'
    # filename = 'your-json-filename.json'
    # s3object = s3.Object(bucket_name, filename)
    # s3object.put(
    #     Body=(bytes(json.dumps(final_dict).encode('UTF-8')))
    #     )
    return final_list
