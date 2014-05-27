#!/usr/bin/env python
# Paul Sladen <9m-mro@paul.sladen.org> - 2014-05-27
# This programme is hereby placed in the public domain, and may be
# distributed and modified without limit, for any purpose.
#
#  ./pdf-to-csv.py > inmarsat-su-log-redacted.csv
#
# Tool to deterministically extract log records from the redacted
# Signalling Unit logfile distributed in PDF format on 23 May 2014
# and published by Inmarsat and the Malaysia DCA on 27 May 2014:
published_url = 'http://www.dca.gov.my/mainpage/MH370%20Data%20Communication%20Logs.pdf'
sha1_checksum = '7b49c5fdec65055ba0a866ccbe468fd38df0d67d'
file_datetime = '2014-03-27T03:04:37Z'
total_records = 1114

local_filename = 'MH370 Data Communication Logs.pdf'

# The aircraft
callsign = "9M-MRO"
icao_hex = 0x75008F

# Logfile time-stamp format
timestamp_format = "%d/%m/%Y %H:%M:%S.%f"

import subprocess
import hashlib
import re
import time
import urllib2
import os
import sys

def sanity_check(pdf_contents, pdf_checksum, pdftotext):
    # Check the PDF input file you have matches the one used originally
    hasher = hashlib.sha1()
    checksum = hasher.update(pdf_contents)
    assert pdf_checksum == hasher.hexdigest()

    # Check the version of the 'pdftotext' command-line tool matches
    # (other versions of pdftotext will work)
    assert pdftotext == subprocess.check_output(
        ['pdftotext', '-v'],
        stderr=subprocess.STDOUT).splitlines()[0].split(' ', 1)[1]

def timestamp(record):
    # Parse the logfile's timestamp format, for when we need it
    return time.strptime(record.split(',', 1)[0], timestamp_format)

def main():
    global local_filename
    # Use name on command-line if given
    if len(sys.argv) > 1:
        local_filename = sys.argv[1]

    # Do we already have a copy of the Inmarsat PDF?
    if not os.path.isfile(local_filename):
        # If not, fetch the PDF, cache the PDF locally
        connection = urllib2.urlopen(published_url)
        open(local_filename, 'wb').write(connection.read())

    # (Try) to open the local PDF file
    pdf = open(local_filename, 'rb').read()

    # Be deterministic, and check everyone has the same starting point
    # Same input file, and same tools
    sanity_check(pdf, sha1_checksum, pdftotext='version 0.18.4')

    # Convert the "logfile" PDF to a textfile, to start to work from
    # (Note that we could work from the raw PDF stream, or from HTML instead)
    text = subprocess.check_output(['pdftotext', '-layout', local_filename, '-'])
    pages = text.split('\f')

    # Start collecting!
    redacted_records = []

    # Page 1, the introduction, with the real logfile headings
    # Page 1 also carries a full (unredacted) example
    for p in pages[0:1]:
        line = p.splitlines()
        # Recover column headings from within the preamble blurb
        # The middle of the three lines are in split 'Frame Number' and needs a ' ' space retaining
        field_headings = (line[14].lstrip() + ' ' + line[15].lstrip() + line[16].lstrip()).replace(', ',',')
        #csv.append(csv_headings)
        #print csv_headings

        # Cache the only (complete) unredacted log record, from 16:42:04.408
        full_164204_408 = ''.join(map(str.lstrip, line[20:22]))
        assert icao_hex == int(full_164204_408.split(',')[1],8)
        #csv.append(unredacted_164204_408)
        #print `unredacted_164204_408`

    # Page 2, is a page trying to explain doppler correction based on
    # IMU-derived location while failing to mention the existance of
    # the IMU/IMS.

    # Pages 3 .. X, are the redacted log with various degrees of
    # reformatting.
    for p in pages[2:]:
        lines = p.splitlines()
        #for l in lines:
        #    try:
        #        bfo_column = l.index(' BFO') - 2
        #        break
        #    except ValueError: continue        
        #for l in lines:
        #    try:
        #        bto_column = l.index(' BTO') - 2
        #        break
        #    except ValueError: continue
                
        for i in xrange(len(lines)):
            l = lines[i]
            if l.lstrip()[1:].startswith('/03/2014'):
                commas = re.sub('\s{2,}', ',', l.lstrip())
                # Cope with lack of double-space in PDF before 'IOR' in some records
                commas = commas.replace(' IOR', ',IOR')

                # Alternatively, try to look for missing numbers and add commas
                # if (len(l) < bfo_column) or l.find('0x20 - Access Request') > 0:
                #     commas += ','
                # if (len(l) < bto_column) or l.find('0x20 - Access Request') > 0:
                #     commas += ','

                # Cope with vertical line-wrap across three-lines in the PDF
                # (Vertical centreing in spreadsheet cells)
                if lines[i-1].find('0x10 - Log-on Request') >= 0:
                    separated = commas.split(',')
                    # Half of the message appears on the /previous/ text line,
                    # and half on the /following/ line
                    prev_line = lines[i-1].lstrip().rstrip()
                    next_line = lines[i+1].lstrip().rstrip()
                    # Insert where the sixth field would have been
                    separated.insert(6, prev_line + ' ' + next_line)
                    # Reassemble the repaired line
                    commas = ','.join(separated)

                # Add one, or two commas to fill out empty BFO/BTO to nine columns
                # Check that it's only the BFO/BTO columns missing
                missing_fields = 9 - len(commas.split(','))
                assert missing_fields <= 3
                commas += ',' * missing_fields

                redacted_records.append(commas)

    # Space out the redacted data to match the full logfile field layout
    # There are several columns where we don't have the data
    # The only one we can fill out is the ICAO 24-bit AES ID.
    full_records = []
    # Save the SITA Owner for filling the missing field
    owner = full_164204_408.split(',')[2]
    for r in redacted_records:
        field = r.split(',')
        reordered_record = ','.join(field[0:1] + # timestamp
            [oct(icao_hex)[1:]] + # 24-bit octal ICAO AES ID, no leading zero - insert
            [owner] + # Owner - insert
            field[1:4] + # Channel Name, Ocean Region, GES ID
            1 * [''] + # Bearer
            field[4:6] + # Channel ID, Channel Type
            4 * [''] + # Framing
            field[6:7] + # SU Type
            11 * [''] + # (Redacted fields, content and RSST)
            field[7:8] + # BFO
            1 * [''] + # Estimated BER
            field[8:] # BTO
            )
        # Patch in the full-form log entry from the page at the correct place
        if field[0] == full_164204_408.split(',')[0]:
            reordered_record = full_164204_408

        full_records.append(reordered_record)

    # Resort the logfile time order, to cope
    # with the circuit-switch calls being split out
    # into an appendix on the last pages.
    sorted_full_records = sorted(full_records[1:], key=timestamp)

    # Output a sorted, usable .csv logfile
    # in approximately the original logfile format
    assert len(sorted_full_records) == total_records
    sorted_full_records.insert(0, field_headings)
    print '\n'.join(sorted_full_records)

if __name__ == '__main__':
    main()
