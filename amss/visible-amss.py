#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ephem
import datetime
import numpy
import pylab
import math
import operator

minute_step = 6

def main():
    viewable = []
    lines = open('geo.txt','r').read().splitlines()
    for i in xrange(0, len(lines), 3):
        tle = lines[i+0], lines[i+1], lines[i+2]
        if tle[0].find('INMARSAT') == tle[0].find('ALPHASAT') == tle[0].find('MTSAT') == -1:
            continue
        #print  '===================',tle[0],'==================='
        sat = ephem.readtle(*tle)

        sat_alt, sat_az = [], []
        #-36.02,88.57
        o = ephem.Observer()
        o.lat, o.lon = map(numpy.deg2rad,(-36,89))
        o.date = datetime.datetime.now()
        #print dir(o)

        start = datetime.datetime(2014,3,8,0,19)
        for d in [start]:
            o.date = d
            sat.compute(o)
            #print dir(sat), sat.elevation
            lat, lon, azi = map(numpy.rad2deg,(sat.sublat, sat.sublong,sat.alt))
            if azi > 10.0:
                cosparYY = tle[1].split(' ')[2]
                # [20-int((t+50)/100) for t in map(int,[("%03d" % i)[1:] for i in range(49,151)])]
                cosparYYYY = str(20-int((int(cosparYY[0:2])+50)/100)) + cosparYY[0:2] + '-' + cosparYY[2:]
                name = tle[0].strip()
                mtsat1 = 'MTSAT-1R'
                if name.find(mtsat1) >= 0: name = mtsat1
                elif name == 'ALPHASAT': name += ' 4A-F4'

                #print sat.range_velocity, sat.range, lat, lon
                viewable.append((azi, cosparYYYY.strip(),name,lon))
                #print `viewable[-1]`
            continue

            sat_alt.append(numpy.rad2deg(inmarsat_3f1.alt))
            deg = numpy.rad2deg(inmarsat_3f1.az)
            if deg > 180.:
                deg -= 360.
            sat_az.append((deg))

    #print sat_az
    #print dir(inmarsat_3f1)
    print 'elevation,identifier,name,satsublon'
    for p in sorted(viewable,key=operator.itemgetter(0),reverse=True):
        print "%.1f,%s,%s,%.2f" % p

    return

    pylab.subplot2grid((2,4), (0,0), colspan=2)
    pylab.plot(dt, sat_az)
    pylab.ylabel("Azimuth (deg)")
    pylab.xticks(rotation=15)
    pylab.subplot2grid((2,4), (1,0), colspan=2)
    pylab.plot(dt, sat_alt)
    pylab.ylabel("Altitude (deg)")
    pylab.xticks(rotation=15)

    pylab.subplot2grid((2,4), (0,2), rowspan=2, colspan=2, polar=True)
    pylab.axes(polar=True).set_theta_zero_location("N")
    pylab.axes(polar=True).set_theta_direction(-1)
    pylab.polar(numpy.deg2rad(sat_az), 90-numpy.array(sat_alt))
    pylab.axes(polar=True).annotate(u"64.5°E",
                    xy=(0, 0),
                    horizontalalignment='center',
                    verticalalignment='center')
    pylab.axes(polar=True).annotate('\n'.join((tle[0],str(start))),
                    xy=(math.pi, 1),
                    horizontalalignment='center',
                    verticalalignment='center')
    for t, az, alt in zip(dt, numpy.deg2rad(sat_az), 90-numpy.array(sat_alt)):
        if t.minute == 0:
            ts = t.strftime('%H:%M')
            if az <= 0.01: h = 'right'
            else: h = 'left'
            pylab.axes(polar=True).annotate(ts,
                    xy=(az, alt),
                    xytext=(az*3-0.03, alt),
                    horizontalalignment=h,
                    verticalalignment='bottom')
    pylab.ylim(0,2)
    pylab.axes(polar=True).set_xticklabels(['N', '', 'E', '', 'S', '', 'W', ''])
    pylab.axes(polar=True).set_yticklabels(['', '', '', ''])

    pylab.savefig('positions.pdf')
    pylab.show()

if __name__=='__main__':
    main()
