#!/usr/bin/env python
# curl -X POST 'http://api.fr24.com/api/common/v1/json-rpc/' -X POST -d '{"jsonrpc":"2.0","method":"Aircraft.doGetPlaybackSingle","params":[47716903],"id":1}' -o fr24-pinned-47716903.json

import os
import json
import urllib2

local_filename = '9m-mro-ads-b.json'

def main():
    if not os.path.isfile(local_filename):
	json_rpc = {'Content-Type': 'application/json-rpc'}
	api = 'http://api.fr24.com/api/common/v1/json-rpc/'
	post = json.dumps({
		'jsonrpc': "2.0",
		'method': "Aircraft.doGetPlaybackSingle",
		'params': [47716903],
		'id': 2
	    })
	conn = urllib2.Request(url=api, data=post, headers=json_rpc)
	raw = urllib2.urlopen(conn, data=post).read()
	j = json.loads(raw)
	assert j['result']['success'] == True
	assert j['result']['data']['aircraft'][2] == '9M-MRO'
	open(local_filename, 'w').write(raw)

    j = json.loads(open(local_filename, 'r').read())
    d = j['result']['data']
    pinned, icao_address, registration = d['aircraft'][:3]
    icao_address = int(icao_address, 16)
    assert icao_address == 0x75008f
    assert registration == '9M-MRO'
    track = d['track']

    keys = 'lat,lon,altitude_ft,velocity,bearing,squawk,seconds,receiver'.split(',')
    for t in track:
        kv = dict(zip(keys,t))
        #lat,lon,altitude_ft,velocity,bearing,squawk,seconds,receiver = t
        print `kv`

if __name__=='__main__':
    main()
