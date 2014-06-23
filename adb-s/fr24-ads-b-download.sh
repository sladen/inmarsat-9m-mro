#!/bin/sh
curl -X POST 'http://api.fr24.com/api/common/v1/json-rpc/' -X POST -d '{"jsonrpc":"2.0","method":"Aircraft.doGetPlaybackSingle","params":[47716903],"id":1}' -o fr24-pinned-47716903.json
