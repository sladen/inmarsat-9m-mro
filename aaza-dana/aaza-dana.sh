#!/bin/sh
#  -x track,speed,course
echo 'c5c93ca2092aea61c2bf247f76ff95f7d692f91e  MH370.gdb' | sha1sum -c - && \
gpsbabel -t -i gdb -f MH370.gdb \
  -x nuketypes,waypoints,routes \
  -x track,start=201403071600,stop=201403080201 \
  -x track,title="Azaa Dana GPS extract 2014-03-07 16:00 to 2014-03-08 02:01" \
  -o gpx -F - \
| sed -e 's/^\(<time>\).*\(<\/time>\)$/\12014-03-07T16:00:00Z\2/' \
| grep -v creator= \
> aaza-dana.gpx

