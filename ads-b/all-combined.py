#!/usr/bin/env python
# Combine The three data-sets from Planefinder, Flightaware and FR24

import json
import csv
import operator

fa_facilities = {'zH': 'WMKK',
                 'cf': 'WMKF',
                 'cC': 'WMSA',
                 'fx': 'WMKP'}

def main():
    records = []
    fa = csv.DictReader(open('fa-database-dump.csv', 'r'))
    for r in fa:
        records.append([int(r['clock']),
                        fa_facilities[r['facility']],
                        r['squawk'],
                        int(r['alt']),
                        r['lat'],
                        r['lon'],
                        r['heading'], # course
                        r['gs'], # sog
                        'flightaware',
                        ])
    # [[u'B772', u'75008F', u'9M-MRO', u'MAS370', u'MH370', 3.0928, 101.765, 10775, 25, 331, u'1394210819', u'2157',
    pf = json.load(open('pf-ads-b-extracted.json', 'r'))
    for r in pf:
        records.append([int(r[10]),
                        '',
                        r[11],
                        r[7],
                        r[5],
                        r[6],
                        r[8],
                        r[9],
                        'planefinder',
                        ])

    # [2.7983, 101.689, 1500,183,328,"2157",1394210550,"F-WMSA2"]
    fr = json.load(open('fr24-pinned-47716903.json','r'))
    # http://forum.flightradar24.com/threads/6080-The-letters-in-front-of-the-ICAO-code%C2%A0#post36507
    for r in fr['result']['data']['track']:
        network,receiver = 'fr24',r[7]
        if receiver.startswith('T-'):
            network += '-home'
            receiver = receiver[2:]
        elif r[7].startswith('F-'):
            network += '-main'
            receiver = receiver[2:]
        records.append([r[6], # time
                        receiver, # receiver
                        r[5], # squawk
                        r[2], # alt
                        r[0], # lat
                        r[1], # lon
                        r[4], # course
                        r[3], # sog
                        network,
                        ])

    w = csv.writer(open('all-combined.csv', 'w'), lineterminator='\n')
    w.writerow(['time','receiver', 'squawk','alt', 'lat','lon', 'course','sog', 'network'])

    # sort by time, then altitude
    records.sort(key=operator.itemgetter(0, 3))

    # The combined data sets contain two records for 1394211254
    # The two lat,lons pairs are 219 metres apart, which at 440knots, is 0.97s!
    # This means that the first one must be very close to 16:54:14.000
    # and the second one must be very close to 16:54:14.999; there are therefore
    # the only two where we reasonably provide their provenance to greater to
    # ~0.005 second (rather than +/- 0.5 seconds for the rest).
    #
    # Given the precision of these two timestamps, it seems reasonable to increment
    # the second one by <=3 milliseconds milliseconds into the start of the next second...
    i = map(operator.itemgetter(0),records).index(1394211254)
    assert records[i][0] == records[i+1][0]
    records[i+1][0] += 1

    # and dump it out
    for i in records:
        w.writerow(i)

if __name__=='__main__':
    main()
