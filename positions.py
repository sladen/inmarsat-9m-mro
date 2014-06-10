#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ephem
import datetime
import numpy
import pylab
import math

minute_step = 6

def main():
    lines = open('sat23839.txt','r').read().splitlines()
    tle = lines[1].lstrip(), lines[7], lines[8]
    inmarsat_3f1 = ephem.readtle(*tle)
    print `inmarsat_3f1`

    sat_alt, sat_az = [], []
    o = ephem.Observer()
    o.lat = numpy.deg2rad(0)
    o.lon = numpy.deg2rad(64.5)
    o.date = datetime.datetime.now()
    print dir(o)

    start = datetime.datetime(2014,03,07,16,00)
    dt = [start + datetime.timedelta(minutes=minute_step*x) for x in range(0, int(8.5*60/minute_step))]
    for d in dt:
        o.date = d
        inmarsat_3f1.compute(o)
        print inmarsat_3f1.range_velocity, inmarsat_3f1.range, map(numpy.rad2deg,(inmarsat_3f1.sublat, inmarsat_3f1.sublong))
        sat_alt.append(numpy.rad2deg(inmarsat_3f1.alt))
        deg = numpy.rad2deg(inmarsat_3f1.az)
        if deg > 180.:
            deg -= 360.
        sat_az.append((deg))
    #print sat_az
    #print dir(inmarsat_3f1)

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
