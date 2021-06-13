import argparse
import json

import websocket


argparser = argparse.ArgumentParser()
argparser.add_argument('--endpoint', required=True)
argparser.add_argument('--controller-key', dest='controller_key', required=True)


def main(args):
    ws = websocket.WebSocket()
    ws.connect(args.endpoint, header={
        'X-Controller-Key': args.controller_key,
    })

    try:
        ws.send(json.dumps({ 'requestType': 'listConnections' }))
        connections = json.loads(ws.recv()).get('connections', [])
        for connection in connections:
            print(f'- {connection["connectionId"]}')

        target_connection_id = input('Target connection >>> ')
        while True:
            command = input("Command >>> ")
            ws.send(json.dumps({
                'requestType': 'command',
                'target': target_connection_id,
                'command': command,
            }))
            result = json.loads(ws.recv()).get('result', '')
            print(result)
    except KeyboardInterrupt:
        print('Exit shell.')
    finally:
        ws.close()


if __name__ == '__main__':
    args = argparser.parse_args()
    main(args)
