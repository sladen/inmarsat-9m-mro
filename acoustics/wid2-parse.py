#!/usr/bin/env python
import gzip
import struct

"""
WID2 2014/03/08 00:00:00.000 H08S1 EDH US   INT  1800077  250.000868  5.420e-04   0.100 HITEC    0.0  0.0
STA2 BN         -7.64530   72.47440 WGS84        -1.88 1.413
DAT2
"""

def read_wid2(f):
    # http://gfzpublic.gfz-potsdam.de/pubman/item/escidoc:4007:7/component/escidoc:4008/Chapter_10_rev1.pdf
    wid2 = f.readline().strip()
    wid2_format = "4sx23sx5sx6s3x3s2x7sxx10sxx9s3x11s4x3s2x3s"
    wid2_unpacked = struct.unpack(wid2_format, wid2)
    sta2 = f.readline().strip()
    sta2_format = "4sx2s9x8s3x8sx5s8x5sx5s"
    sta2_unpacked = struct.unpack(sta2_format, sta2)
    dat2_unpacked = (f.readline().strip(),)
    count = int(wid2_unpacked[5])
    # minus one byte to avoid the last \n creating an empty line.
    samples = map(int,f.read((count)*8-1).split('\n'))
    # skip newline.
    f.readline()
    chk2_unpacked = struct.unpack("4sx8s",f.readline().strip())
    return (wid2_unpacked, sta2_unpacked, dat2_unpacked, samples, chk2_unpacked)


def main():
    # HA08S, three channels, 250Hz
    f = gzip.open('bdsAutodrm-pnOwJj.gz','r')
    channels = [read_wid2(f) for i in xrange(3)]

if __name__=='__main__':
    main()
