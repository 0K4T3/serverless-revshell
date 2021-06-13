import argparse
import json
import subprocess

import websocket


argparser = argparse.ArgumentParser()
argparser.add_argument('--endpoint', required=True)


def on_message(ws, message):
    payload = json.loads(message)
    output = subprocess.check_output(payload['command'].split(' '))
    print(payload['command'])
    print(output)
    ws.send(json.dumps({
        'controller': payload['controller'],
        'result': output.decode(),
    }))


def main(args):
    ws = websocket.WebSocketApp(
        args.endpoint,
        on_message=on_message,
    )
    ws.run_forever()


if __name__ == '__main__':
    args = argparser.parse_args()
    main(args)
