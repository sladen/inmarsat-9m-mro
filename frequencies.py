#!/usr/bin/env python

import csv
import itertools
import operator

# http://stackoverflow.com/questions/2931672/what-is-the-cleanest-way-to-do-a-sort-plus-uniq-on-a-python-list
def sort_uniq(sequence, sort=operator.itemgetter(3)):
    return itertools.imap(
        operator.itemgetter(0),
        itertools.groupby(sorted(sequence, key=sort)))

def main():
    transmissions = []
    c = csv.DictReader(open('inmarsat-su-log-redacted.csv', 'r'))
    for d in c:
        encoding = d['Channel Type'][0]
        direction = d['Channel Type'][-2:]
        unit = int(d['Channel Unit ID'])
        channel_number_field = 1
        rate_field = 2
        if encoding == 'C':
            # IOR-3730-21000
            channel_number = int(d['Channel Name'].split('-')[1],16)
            rate = int(d['Channel Name'].split('-')[2])
        else:
            # IOR-P10500-0-3859
            channel_number = int(d['Channel Name'].split('-')[3],16)
            rate = int(d['Channel Name'].split('-')[1][1:])
        # http://www.icao.int/safety/acp/Inactive%20working%20groups%20library/ACP-WG-M-Iridium-8/IRD-SWG08-WP07%20-%20Old_AMSS_material_Ch.4_plus_Attachment.doc
        # Paired spectrum 101.5MHz apart
        # base offsets are 1510Mhz and 1611.5MHz
        frequency = channel_number * 0.0025 + 1510
        if direction == 'RX': frequency += 101.5
        transmissions.append((direction, encoding, channel_number, frequency, rate, unit))

    #for t in sort_uniq(transmissions):
    #    print "%s, %s, %d, %9.4f, %5d, %2d" % t

    print 'Count,Direction,Encoding,Channel Number,Frequency,Rate,Unit ID'
    for t,g in itertools.groupby(sorted(transmissions, key=operator.itemgetter(3))):
        print "%3d, %s, %s, %d, %9.4f, %5d, %2d" % ((len(list(g)),) + t)

if __name__=='__main__':
    main()
