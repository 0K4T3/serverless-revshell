import datetime
import json

import boto3


class Connection(object):
    ENDPOINT_URL = ''

    def __init__(self, connection_id: str, connected_at: str, source_ip: str, is_controller: bool):
        self.connection_id = connection_id
        self.connected_at = connected_at
        self.source_ip = source_ip
        self.is_controller = is_controller
        self.apigw_management = boto3.client('apigatewaymanagementapi', endpoint_url=self.ENDPOINT_URL)

    def to_json(self):
        return {
            'connectionId': self.connection_id,
            'connectedAt': self.connected_at,
            'sourceIp': self.source_ip,
        }

    def post_message(self, message: dict):
        self.apigw_management.post_to_connection(
            ConnectionId=self.connection_id,
            Data=json.dumps(message).encode(),
        )


class ConnectionManager(object):
    TABLE_NAME = 'serverlessRevshellConnections'

    def __init__(self):
        self._table = boto3.resource('dynamodb').Table(self.TABLE_NAME)

    def new_connection(self, connection_id: str, source_ip: str, is_controller: bool):
        self._table.put_item(
            Item={
                'ConnectionId': connection_id,
                'ConnectedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'SourceIp': source_ip,
                'IsController': is_controller,
            }
        )

    def get_connection(self, connection_id: str) -> Connection:
        item = self._table.get_item(
            Key={
                'ConnectionId': connection_id,
            }
        ).get('Item', {})
        return self._create_connection_instance(item)

    def list_node_connections(self) -> list:
        return [
            self._create_connection_instance(item)
            for item in self._table.scan().get('Items', [])
            if not item.get('IsController', False)
        ]

    def delete_connection(self, connection_id: str):
        self._table.delete_item(
            Key={
                'ConnectionId': connection_id,
            }
        )

    def _create_connection_instance(self, item) -> Connection:
        return Connection(
            connection_id=item.get('ConnectionId', ''),
            connected_at=item.get('ConnectedAt', ''),
            source_ip=item.get('SourceIp', ''),
            is_controller=item.get('IsController', False),
        )
