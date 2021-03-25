import time
import json
import boto3


def str_decode(val):
    val = val.split('\n')
    ip_adress = val[0]
    launch_time = val[1]
    uptime = int(float(val[2].split(' ', 1)[0]))
    os_version = val[4]
    return ip_adress, launch_time, uptime, os_version
    
def lambda_handler(event, context):

    # boto3 client
    client = boto3.client('ec2')
    ssm = boto3.client('ssm')
    s3 = boto3.resource('s3')
    
    # getting instance information and ssm instance information
    describeInstance = client.describe_instances()
    ssm_describeInstance = ssm.describe_instance_information()
    ssm_instances = [i['InstanceId'] for i in ssm_describeInstance['InstanceInformationList']]
    
    print(ssm_instances)
    
    InstanceId=[]
    # fetchin instance id of the running instances
    for i in describeInstance['Reservations']:
        for instance in i['Instances']:
            if instance["State"]["Name"] == "running":
                InstanceId.append(instance['InstanceId'])
    final_list = []

    # looping through instance ids
    try:
        for instanceid in InstanceId:
            # command to be executed on instance
            response = ssm.send_command(
                InstanceIds=[instanceid],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': ['hostname -i; uptime -s; cat /proc/uptime; cat /etc/*_version']})
                    
            # fetching command id for the output
            json_response = response['Command']['CommandId']
            time.sleep(3)

            # fetching command output
            json_output = ssm.get_command_invocation(
                CommandId=json_response,
                InstanceId=instanceid
                )
            
            ip_address, launch_time, uptime, os_version = str_decode(str(json_output['StandardOutputContent']))
            # print(ip_address, launch_time, uptime, os_version)
            # print(json_output['InstanceId'])
            
            if uptime < 1800:
                temp_list = [
                    json_output['InstanceId'],
                    ip_address,
                    launch_time,
                    uptime,
                    os_version
                ]
                final_list.append(tuple(temp_list))
        s3object = s3.Object('paradoxtestingbucket', 'demo.json')
        s3object.put(
            Body=(bytes(json.dumps(final_list).encode('UTF-8')))
        )
    except:
        pass
    
    return final_list
