#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sgp4
import sgp4.io
import sgp4.earth_gravity

def main():
    lines = open('geo.txt','r').read().splitlines()
    for i in xrange(0,len(lines),3):
        tle = lines[i+0], lines[i+1], lines[i+2]
        sat = sgp4.io.twoline2rv(tle[1], tle[2], sgp4.earth_gravity.wgs72)
        position, velocity = sat.propagate(2014, 03, 8, 00, 00, 00)
        print tle[0], position, velocity

if __name__=='__main__':
    main()
