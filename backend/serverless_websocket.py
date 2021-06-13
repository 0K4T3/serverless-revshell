import json


class WebSocketRequest(object):
    def __init__(self, context = None, headers = None, body = None):
        self.context = context
        self.headers = headers
        self.body = body


class WebSocketResponse(object):
    def __init__(self, status_code: int, body = None):
        self.status_code = status_code
        self.body = {} if not body else body

    def to_lambda_response(self) -> dict:
        return {
            'statusCode': self.status_code,
            'body': json.dumps(self.body),
        }


class ServerlessWebsocket(object):
    def __init__(self, on_connect = None, on_disconnect = None, on_message = None):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_message = on_message

    def dispatch(self, event, context):
        req = WebSocketRequest(
            context=event.get('requestContext', {}),
            headers=event.get('headers', {}),
            body=json.loads(event.get('body', '{}')),
        )
        event_type = req.context.get('eventType', '').lower()
        handler = getattr(self, f'on_{event_type}')
        res = WebSocketResponse(status_code=404)
        if handler:
            res = handler(req)
        return res.to_lambda_response()

