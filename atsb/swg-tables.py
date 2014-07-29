#!/usr/bin/env python
# Paul Sladen, 29 July 2014.  Public Domain.
#
# Extract csv tables from .docx version of the ATSB search area
# definition report.  Inside are EMF (vector) images of the tables
# supplied by the Satellite Working Group (== Inmarsat).
# This does not currently work on the first two tables that have
# two sub-tables side-by-side in one EMF image.

# uses PyEMF: http://sourceforge.net/projects/pyemf/files/

# http://www.atsb.gov.au/media/5243942/ae-2014-054_mh370_searchareas.pdf
# sha1sum 9767fc7cccde9cd51a311ca56e9219e8a3778833
source = 'ae-2014-054_mh370_searchareas_v2.docx'

import zipfile
import glob
import StringIO
import pyemf
import itertools
import operator
import csv
#import bisect

def main():
    candidates = ['word/media/image%02d.emf' % n for n in xrange(45, 51)]
    z = zipfile.ZipFile(source)
    for f in z.infolist():
        if f.filename in candidates:
            print 'Trying to parse', f.filename,
            if True:
                #print f.filename, len(z.read(f.filename))
                # Kludge because of PyEMF API limitations
                # Do the equivalent of the internals of EMF.load(),
                # but manually, and without presuming any filename.
                e = pyemf.EMF()
                e.filename, e.records = f.filename, []
                e._unserialize(StringIO.StringIO(z.read(f.filename)))
                e.scaleheader = False
                e.dc.getBounds(e.records[0])

                def txt(r, minimum=None, maximum=None):
                    test = False
                    if r.__class__.__name__ in ('_EXTTEXTOUTW'):
                        test = True
                        if minimum is not None and r.values[1] < minimum:
                            test = False
                        if maximum is not None and r.values[1] > maximum:
                            test = False
                    return test

                # Use the position of the horizontal rules in the table to split into three sections
                ruled_lines = sorted([r.values[1] for r in e.records if r.__class__.__name__ in ('_LINETO')])
                if len(sorted(set(ruled_lines))) != 3:
                    # Still need to cope with "split tables" by parsing left/right halves separately
                    print
                    continue

                header_min, header_max, footer_min = sorted(set(ruled_lines))
                #print [(r.values[0:2], r.string.decode('utf-16le')) for r in e.records if txt(r, maximum=footer_min)]
                #print [(r.values[0:2], r.string.decode('utf-16le')) for r in e.records if txt(r, header_min, header_max)]
                title = [(r.values[0:2], r.string.decode('utf-16le')) for r in e.records if txt(r, maximum=header_min)]
                headings = [(r.values[0:2], r.string.decode('utf-16le')) for r in e.records if txt(r, minimum=header_min, maximum=header_max)]
                values = [(r.values[0:2], r.string.decode('utf-16le')) for r in e.records if txt(r, minimum=header_max, maximum=footer_min)]

                #print [r.string.decode('utf-16le') for r in e.records if txt(r, minimum=header_min, maximum=header_max)]
                # Figure out which line is the one with the most field headings on.
                def fix_y(x):
                    r = x[0][1]
                    # hack for misalignment in "Table 2"
                    if r in (42, 63): r += 2
                    return r
                h1 = sorted(headings, key=fix_y)
                h2 = itertools.groupby(h1, key=fix_y)
                m = 0
                max_k = None
                for k, g in h2:
                    l = len(list(g))
                    if m < l:
                        m = l
                        max_k = k
                #print max_k, 'is the line with the most field headings'

                # Build the field-headings based on the line with the most
                # Compile a list of those that appear in the longest line of field headings
                valid_x = [h[0][0] for h in headings if abs(h[0][1] - max_k) <= 2]
                valid_headings = [h for h in h1 if h[0][0] in valid_x]
                
                #for i in [(r.values, r.string.decode('utf-16le')) for r in e.records if txt(r, minimum=header_min, maximum=header_max)]:

                #print title, headings, values
                # Sort and group by X position
                #h1 = sorted(valid_headings, key=lambda x: (x[0][0]))
                #h2 = itertools.groupby(h1, key=lambda x: x[0][0])
                def floor_x(x):
                    #valid_x_wider = valid_x + valid_x[-1:]
                    #new_x = valid_x_wider[bisect.bisect_right(valid_x, x[0][0])-1]
                    new_x = min(valid_x, key=lambda z:abs(z-x[0][0]))
                    #print valid_x, x[0][0], new_x, x[1], bisect.bisect_left(valid_x, x[0][0])
                    #print 'floor_x(new,old)', x[0][0],y
                    return new_x

                h1 = sorted(headings, key=floor_x)
                h2 = itertools.groupby(h1, key=floor_x)

                final_headings = []
                for k,g in h2:
                    final_headings.append(' '.join([x[1] for x in sorted(list(g), key=lambda x:x[0][1])]))
                #print final_headings, len(final_headings)
                table = [final_headings]
                for k,g in itertools.groupby(values, key=lambda x: x[0][1]):
                    row = [v[1] for v in g]
                    # pad any missing columns up to end
                    row += [u''] * (len(final_headings)-len(row))
                    table.append(row)
                #print table

                # make a useful filename without weird characters in it
                filename = title[0][1].lower().replace(' ', '-') + '.csv'
                for c in ':()':
                    filename = filename.replace(c, '')
                print '->', filename

                # dump out the extracted table
                w = csv.writer(open(filename, 'w'), lineterminator='\n')
                for row in table:
                    w.writerow([s.encode('utf-8') for s in row])
                    
if __name__=='__main__':
    main()
