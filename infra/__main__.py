import json

import pulumi
import pulumi_aws as aws

config = {}
with open('./config.json') as fp:
    config = json.load(fp)

APP_NAME = config['AppName']
LAMBDA_ROLE = config['LambdaRole']

connection_table = aws.dynamodb.Table(
    f'{APP_NAME}Connections',
    name=f'{APP_NAME}Connections',
    attributes=[
        aws.dynamodb.TableAttributeArgs(
            name='ConnectionId',
            type='S',
        ),
    ],
    billing_mode='PROVISIONED',
    hash_key='ConnectionId',
    read_capacity=5,
    write_capacity=5,
)

ws_handler = aws.lambda_.Function(
    f'{APP_NAME}WebsocketHandler',
    role=LAMBDA_ROLE,
    runtime='python3.8',
    handler='app.lambda_handler',
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./initial_code'),
    }),
)

ws_api = aws.apigatewayv2.Api(
    f'{APP_NAME}WebsocketAPI',
    protocol_type='WEBSOCKET',
    route_selection_expression='$request.body.action',
)

lambda_integration = aws.apigatewayv2.Integration(
    f'{APP_NAME}LambdaIntegration',
    api_id=ws_api.id,
    integration_type='AWS_PROXY',
    connection_type='INTERNET',
    content_handling_strategy='CONVERT_TO_TEXT',
    integration_method='POST',
    integration_uri=ws_handler.invoke_arn,
    passthrough_behavior='WHEN_NO_MATCH',
)

connect_route = aws.apigatewayv2.Route(
    f'{APP_NAME}ConnectRoute',
    api_id=ws_api.id,
    route_key='$connect',
    target=lambda_integration.id.apply(lambda integration_id: 'integrations/' + integration_id),
)

disconnect_route = aws.apigatewayv2.Route(
    f'{APP_NAME}DisconnectRoute',
    api_id=ws_api.id,
    route_key='$disconnect',
    target=lambda_integration.id.apply(lambda integration_id: 'integrations/' + integration_id),
)

default_route = aws.apigatewayv2.Route(
    f'{APP_NAME}DefaultRoute',
    api_id=ws_api.id,
    route_key='$default',
    target=lambda_integration.id.apply(lambda integration_id: 'integrations/' + integration_id),
)

stage = aws.apigatewayv2.Stage(
    f'{APP_NAME}APIStage',
    api_id=ws_api.id,
    auto_deploy=True,
)

invoke_permission = aws.lambda_.Permission(
    f'{APP_NAME}LambdaPermission',
    action='lambda:invokeFunction',
    function=ws_handler.name,
    principal='apigateway.amazonaws.com',
    source_arn=stage.execution_arn.apply(lambda arn: arn + '*/*'),
)

pulumi.export('api_endpoint', ws_api.api_endpoint)
pulumi.export('api_invoke_url', stage.invoke_url)
