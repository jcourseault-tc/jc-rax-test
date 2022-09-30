import json
import logging
import boto3


MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger('SsenseLambdaLogger')
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    event_type = event['headers']['x-github-event']
    event_body = json.loads(event['body'])
    github_owner = event_body['repository']['owner']['login']
    github_repo = event_body['repository']['name']
    branch_name = event_body['ref']
    ref_type = event_body['ref_type']
  
    
    # if github_repo != "" or ref_type != 'branch':
    #     quit()
    
    event_details = { 'owner': github_owner, 'repo_name':github_repo,  'event_type': event_type, 'branch_name':branch_name  }
    logger.info(event_details)
 
        
    if event_type == "create":
        cf_client = boto3.client('cloudformation')
        cf_client.create_stack(
            StackName=f'{github_repo}-{branch_name}-pipeline',
            TemplateURL=f'https://rax-ah-ssense-artifacts.s3.us-west-2.amazonaws.com/cfn/code-pipeline-cfn.yaml',
            
            Parameters=[
                {
                    'ParameterKey': 'EnvironmentType',
                    'ParameterValue': "qa"
                },
                {
                    'ParameterKey': 'ArtifactsBucket',
                    'ParameterValue': "rax-ah-ssense-artifacts"
                },
                {
                    'ParameterKey': 'GitHubOwner',
                    'ParameterValue': github_owner
                },
                {
                    'ParameterKey': 'GitHubRepo',
                    'ParameterValue': github_repo
                },
                {
                    'ParameterKey': 'GitHubBranch',
                    'ParameterValue': branch_name
                }
            ],
            OnFailure='ROLLBACK',
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
    else:
        cf_client = boto3.client('cloudformation')
        cf_client.delete_stack(
            StackName=f'{github_repo}-{branch_name}-pipeline'
        )