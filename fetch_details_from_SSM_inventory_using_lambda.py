# References
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.list_inventory_entries
# https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-inventory-schema.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html
# https://github.com/4nur4g/AWS_Tutorial/blob/main/fetch_onlineSSSM_instance_details_using%20lambda.py
'''
In this function we are extracting SSM Agent installed
EC2 instances installed applications using SSM inventory
Guidelines:
    1: InstanceId : we will have to provide
'''
import json
import boto3

def lambda_handler(event, context):
    # boto3 client
    final_list = []
    final_dict = {}
    ssm = boto3.client('ssm')
            
    # getting inventory details Applications installed
    inventory = ssm.list_inventory_entries(
        InstanceId=['InstanceId'],
        TypeName='AWS:Application'
        )
    final_dict['Applications'] = inventory['Entries']
    final_list.append(final_dict.copy())
                
    return final_list
