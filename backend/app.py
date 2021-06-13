import logging
import os
import traceback

from connection import (
    Connection,
    ConnectionManager,
)
from serverless_websocket import (
    ServerlessWebsocket,
    WebSocketRequest,
    WebSocketResponse,
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)


controller_key = os.getenv('CONTROLLER_KEY', '')
api_endpoint_url = os.getenv('API_ENDPOINT_URL', '')


Connection.ENDPOINT_URL = api_endpoint_url


def on_connect(req: WebSocketRequest) -> WebSocketResponse:
    logger.info('on connect')

    connection_id = req.context.get('connectionId', '')
    source_ip = req.context.get('identity',{}).get('sourceIp', '')
    req_controller_key = req.headers.get('X-Controller-Key', '')
    is_controller = req_controller_key == controller_key

    try:
        connection_manager = ConnectionManager()
        connection_manager.new_connection(
            connection_id,
            source_ip,
            is_controller,
        )
        return WebSocketResponse(status_code=200)
    except Exception as e:
        logger.error(traceback.format_exc())
        return WebSocketResponse(status_code=500, body={'message': str(e)})


def on_disconnect(req: WebSocketRequest) -> WebSocketResponse:
    logger.info('on disconnect')
    connection_id = req.context.get('connectionId', '')

    try:
        connection_manager = ConnectionManager()
        connection_manager.delete_connection(connection_id)
        return WebSocketResponse(status_code=200)
    except Exception as e:
        logger.error(traceback.format_exc())
        return WebSocketResponse(status_code=500, body={'message': str(e)})


def on_message(req: WebSocketRequest) -> WebSocketResponse:
    logger.info('on message')

    messanger_connection_id = req.context.get('connectionId', '')

    connection_manager = ConnectionManager()
    messanger_connection = connection_manager.get_connection(messanger_connection_id)

    try:
        target_connection = None
        message = {}
        if messanger_connection.is_controller:
            logger.info(req.body)
            if req.body['requestType'] == 'listConnections':
                connections = connection_manager.list_node_connections()
                target_connection = messanger_connection
                message = {
                    'connections': [conn.to_json() for conn in connections],
                }
            if req.body['requestType'] == 'command':
                target_connection = connection_manager.get_connection(req.body['target'])
                message = {
                    'command': req.body['command'],
                    'controller': messanger_connection_id,
                }
        else:
            target_connection = connection_manager.get_connection(req.body['controller'])
            message = {
                'result': req.body['result'],
            }

        target_connection.post_message(message)
        return WebSocketResponse(status_code=200)
    except Exception as e:
        logger.error(traceback.format_exc())
        return WebSocketResponse(status_code=500, body={'message': str(e)})


def lambda_handler(event, context):
    logger.info(event)
    websocket = ServerlessWebsocket(
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        on_message=on_message,
    )
    return websocket.dispatch(event, context)

