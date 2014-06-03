#!/usr/bin/env python
# http://mcleodsean.wordpress.com/2014/04/25/mh-370-forward-tracking/
import math

earthRadius = 6371.0

def sphericalToECEF(latlon):
    lat, lon = latlon

    theta = lon
    phi = 90 - lat

    x = earthRadius * math.sin(math.radians(phi)) * math.cos(math.radians(theta))
    y = earthRadius * math.sin(math.radians(theta)) * math.sin(math.radians(phi))
    z = earthRadius * math.cos(math.radians(phi))

    return (x,y,z)

# Haversine great circle distance calculation for spherical earth
def greatCircleDistance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = earthRadius 

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def greatCircleDestination(latlon, bearing, dist):
    R = earthRadius
    lat1, lon1 = latlon
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    bearing = math.radians(bearing)
    lat2 = math.asin(math.sin(lat1)*math.cos(dist/R) + math.cos(lat1)*math.sin(dist/R)*math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(dist/R)*math.cos(lat1), math.cos(dist/R)-math.sin(lat1)*math.sin(lat2))
    
    return math.degrees(lat2), math.degrees(lon2)

def LOSSpeed(pos1, vel1, pos2, vel2):
    P = (pos1[0]-pos2[0], pos1[1]-pos2[1], pos1[2]-pos2[2])
    V = (vel1[0]-vel2[0], vel1[1]-vel2[1], vel1[2]-vel2[2])

    # LOS = (V dot P)/|P|

    VdotP = V[0]*P[0] + V[1]*P[1] + V[2]*P[2]
    Pbar = math.sqrt(P[0]*P[0] + P[1]*P[1] + P[2]*P[2])

    return VdotP / Pbar

def ecefVelocities(latlon, speed, bearing):
    x,y,z = sphericalToECEF(latlon)

    latCircum = earthRadius * math.cos(math.radians(latlon[0])) * math.pi * 2.0
    equCircum = earthRadius * math.pi * 2.0

    lonDistance = speed * math.sin(math.radians(bearing))
    latDistance = speed * math.cos(math.radians(bearing))

    thetaDot = (lonDistance / latCircum) * 2 * math.pi
    phiDot = (latDistance / equCircum) * 2 * math.pi

    x2,y2,z2 = sphericalToECEF((latlon[0]+math.degrees(phiDot), latlon[1]+math.degrees(thetaDot)))

    return (x2-x, y2-y, z2-z)

def knotsToKms(knots):
    return (knots * 1.852)/(3600.0)

def nmToKm(nm):
    return nm * 1.852

def kmToNm(km):
    return km / 1.852

