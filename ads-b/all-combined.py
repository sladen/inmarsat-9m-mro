#!/usr/bin/env python
# Combine The three data-sets from Planefinder, Flightaware and FR24
# Paul Sladen, 2014
#
# The original purpose was to provide consoldiated comparitive
# roc,sog,course and coordinate data for BFO bias calibation.
#
# Following on-going confusion into 2016 around the very final points
# picked up by the 'fr24-main' network, unreliable/suspect fields that
# may have arisen from from repeating of previous data have been more
# brutally filtered.
#
# In particular, the very last packet received is likely to have been
# Mode-A or Mode-C only, and therefore only containing Squawk rather
# than ADS-B or Extended Squitter.

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
                        '',
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
                        '',
                        'planefinder',
                        ])

    fr24 = {}
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
        # nuke expolated low-precision latlon (less that two decimal places)
        lat, lon, alt = map(str,r[0:3])
        if (len(lat) - lat.rindex('.') - 1) <= 2:
            lat, lon, alt = ('',) * 3
        fr24[r[6]] = list([r[6], # time
                        receiver, # receiver
                        r[5], # squawk
                        alt, # alt
                        lat, # lat
                        lon, # lon
                        r[4], # course
                        r[3], # sog
                        '', # roc
                        network,
                        ])

    # ["75008F", 2.81, 101.68, 327, 1700, 200, "2157", "F-WMSA2", "B772", "9M-MRO", 1394210567, "KUL", "PEK", "MH370", 0, 896, "MAS370", 0]
    fr2 = json.load(open('fr24-time-ads-b-extracted.json','r'))
    for r in fr2:
        # data after 1394212605 are duplicates with no altitude or vertical
        # velocity data
        network,receiver = 'fr24',r[7]
        if receiver.startswith('T-'):
            network += '-home'
            receiver = receiver[2:]
        elif r[7].startswith('F-'):
            network += '-main'
            receiver = receiver[2:]
        timestamp = r[10]
	if timestamp in fr24:
            # Append rate-of-climb if available
            fr24[timestamp][8] = r[15] # roc
            # TODO prove that the alt and lon/lat are the same to 2d.p.
        else:
            # Hide extrapolated fields.
            fr24[timestamp] = ([r[10], # time
                            receiver, # receiver
                            r[6], # squawk
                            '',#r[4], # alt
                            '',#r[1], # lat
                            '',#r[2], # lon
                            r[3], # course
                            r[5], # sog
                            r[15], #roc
                            network,
                            ])

    # Extended squitter or ADS-B is either lon/lat/alt *or* dlon/dlat/roc
    #
    # The later records are only single-sourced from one 'fr24-main' receiver,
    # should be treated even more careful because they cannot be corroborated.
    # Anything that appears to be extrapolation or repeating of stale values
    # should be reasonably assumbed to be so, and filtered out.
    #
    # A generic way of doing this now is to check whether the
    # dlat/dlon fields are identical to the dlat/dlon at the the previous
    # timestamp and to discount on this basis, viz:
    fr24_only_timestamp = 1394212004
    fr24_only_timestamp = 0
    timestamps = sorted([t for t in fr24.keys() if t >= fr24_only_timestamp])
    for t1,t2 in zip(timestamps[:-1], timestamps[1:]):
        # filter out those with non-zero roc, and apparent duplication of previous dlat/dlon data
        if fr24[t2][8] == '' and \
                fr24[t1][6] == fr24[t2][6] and \
                fr24[t1][7] == fr24[t2][7]:
            for velocity_component in 6,7,8: # blank the sog,course,roc
                fr24[t2][velocity_component] = ''

    # The last transmission(s) captured would appear to have been
    # Mode-C (Squawk + but with disabled/null altitude) or Mode-A only
    # (Squawk only) responding to being illuminated by an SSR Radar.
    # This would be consistent with the somewhat vague wording in the
    # subsequently published MDCA "Factual Information" report published
    # on 13 March 2015:
    # http://mh370.mot.gov.my/download/FactualInformation.pdf
    last_fr24_timestamp = 1394212863

    # Remove likely extrapolated/carried-over velocity components
    for velocity_component in 6,7,8: # sog,course,roc
        fr24[last_fr24_timestamp][velocity_component] = ''

    # And save back what we still have left to the main combined log
    records.extend(fr24.values())

    # {"unique_id":"14876470","FNCORR":"MAS370","FCH":"2014-03-07 16:52:04","FCH_TS":"1394211124","FLA":"3.5949","FLO":"102.003","FHD":"26","FAL":"22000","FSQ":"2157","FVR":"1792"},
    rb24 = json.load(open('rb24-flighthistory.json','r'))
    # One receiver ID in records, but only one receiver, so can correct globally
    rb24_clock_drift = +5
    for r in rb24['data']:
        records.append([int(r['FCH_TS']) + rb24_clock_drift,
                        '',
                        r['FSQ'],
                        int(r['FAL']),
                        r['FLA'],
                        r['FLO'],
                        r['FHD'], # course
                        '', # sog
                        r['FVR'],
                        'radarbox24',
                        ])


    w = csv.writer(open('all-combined.csv', 'w'), lineterminator='\n')
    w.writerow(['time','receiver', 'squawk','alt', 'lat','lon', 'course','sog','roc','network'])

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
