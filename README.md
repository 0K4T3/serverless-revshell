# serverless-revshell

"serverless-revshell" is WebSocket reverse shell with serverless architecure.

## Installation

```
$ git clone https://github.com/0K4T3/serverless-revshell.git
```

### Construct infrastructure

※ You should install Pulumi for construct infrastructure with IaaC.

```
$ cd infra
$ pulumi up
```

### Setup backend

```
$ cd backend
$ lambda-uploader
```