#!/usr/bin/env python

# http://krk.fr24.com/playback/20140307/164300.js

import time
import json
import urllib2
from StringIO import StringIO
import gzip


def main():
    api = 'http://krk.fr24.com/playback/20140307/%d00.js'
    start = 1643
    end = 1659

    l = []
    for t in range(start, end):
        buf = StringIO( urllib2.urlopen(api % (t)).read() )
	jsonp = gzip.GzipFile(fileobj=buf).read()
        
	print t
        j = json.loads(jsonp[ jsonp.index("(") + 1 : jsonp.rindex(")") ])
        try:
            l.append(j['2d81a27'])
        except: pass
    open('fr24-time-ads-b-extracted.json', 'w').write('[\n ' + ',\n '.join(map(json.dumps,l)) + '\n]\n')

if __name__=='__main__':
    main()
