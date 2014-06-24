#!/usr/bin/env python

# http://planefinder.net/endpoints/playback/update.php?utc=1394211000&loc=1394211000

import time
import json
import urllib2

def main():
    api = 'http://planefinder.net/endpoints/playback/update.php?utc=%d&loc=%d'
    start = int(time.mktime((2014,3,7,16,46,0,0,0,0)))
    end = int(time.mktime((2014,3,7,17,02,0,0,0,0)))

    l = []
    # Has to be 60-second aligned
    for t in xrange(start, end, 60):
        print time.gmtime(t)
        j = json.load(urllib2.urlopen(api % (t,t)))
        try:
            l.append(j['planes']['75008F'])
        except: pass
    open('pf-ads-b-extracted.json', 'w').write('[\n ' + ',\n '.join(map(json.dumps,l)).replace('3.677', '3.6770') + '\n]\n')

if __name__=='__main__':
    main()
