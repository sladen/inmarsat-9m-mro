#!/bin/sh
API=http://www.radarbox24.com/APIv1
TOKEN="`wget -q -O- $API/guest_init |
gunzip -cd | cut -d\\\" -f4`"
curl -o - -X POST $API/flighthistory' \
-d "fn=MAS370&s=1394210000&e=1394213000&token=$TOKEN" \
| gunzip -cd > rb24-flighthistory.json
