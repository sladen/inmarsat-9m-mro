import math
import Geo
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

''' Comparison with Victor's spreadsheet
aircraftPos = Geo.sphericalToECEF((-38.3313,87.424086))
aircraftVel = Geo.ecefVelocities((-38.3313,87.424086), 0.247293464, 187.812)
los = Geo.LOSSpeed((18173.906276,38051.980584,433.193954), (0.001476,-0.001458,-0.082097), aircraftPos, aircraftVel)
'''

aircraftGroundSpeed = 400
maxAircraftGSAfterLastRadarContact = 520
filterUsingDoppler = True
pingRingDiffError = 0.04
dopplerDiffError = 0.7
bearingIncrement = 1
startingIncrement = 1

# Last radar position at 18:22UTC lat - 6.5381 lon - 96.408
lastAircraftRadarPos = (6.5381, 96.408)
timeFromLastRadarContactTo1940Ping = 78
maxRangeFromLastRadarContactTo1940Ping = (timeFromLastRadarContactTo1940Ping / 60.0) * maxAircraftGSAfterLastRadarContact

satelliteInfo1940 = { 'LatLon': (1.640,64.520), 'XYZ' : (18140.934782,38066.764468,1206.206412), 'Velocity': (0.001663,-0.000776,-0.001656),  'LOSSpeed': Geo.knotsToKms(-53.74), 'NextPingTimeOffset': 60.0, 'PingRadius': Geo.nmToKm(1762), 'Color': 'b', 'Elevation': 55.80 }
satelliteInfo2040 = { 'LatLon': (1.576,64.510), 'XYZ' : (18147.379654,38064.186790,1159.122617), 'Velocity': (0.001811,-0.000618,-0.024394),  'LOSSpeed': Geo.knotsToKms(-70.87), 'NextPingTimeOffset': 60.0, 'PingRadius': Geo.nmToKm(1805), 'Color': 'c', 'Elevation': 54.98 }
satelliteInfo2140 = { 'LatLon': (1.404,64.500), 'XYZ' : (18154.399609,38061.901891,1032.716137), 'Velocity': (0.001962,-0.000627,-0.045468),  'LOSSpeed': Geo.knotsToKms(-84.20), 'NextPingTimeOffset': 60.0, 'PingRadius': Geo.nmToKm(1962), 'Color': 'g', 'Elevation': 52.01 }
satelliteInfo2240 = { 'LatLon': (1.136,64.490), 'XYZ' : (18161.767618,38059.215141,835.616356),  'Velocity': (0.001981,-0.000841,-0.063437),  'LOSSpeed': Geo.knotsToKms(-97.14), 'NextPingTimeOffset': 91.0, 'PingRadius': Geo.nmToKm(2199), 'Color': 'r', 'Elevation': 47.54 }
satelliteInfo0011 = { 'LatLon': (0.589,64.471), 'XYZ' : (18173.906276,38051.980584,433.193954),  'Velocity': (0.001476,-0.001458,-0.082097),  'LOSSpeed': Geo.knotsToKms(-111.18),'NextPingTimeOffset':  0.0, 'PingRadius': Geo.nmToKm(2642), 'Color': 'm', 'Elevation': 39.33 }

satelliteInfos = [satelliteInfo1940, satelliteInfo2040, satelliteInfo2140, satelliteInfo2240, satelliteInfo0011] 

# Calculate starting points on 19:40UTC arc
startingPoints = []
for bearing in range(0, 180, startingIncrement):
    pingRingPos = Geo.greatCircleDestination(satelliteInfo1940['LatLon'], bearing, satelliteInfo1940['PingRadius'])
    if Geo.greatCircleDistance(pingRingPos, lastAircraftRadarPos) < Geo.nmToKm(maxRangeFromLastRadarContactTo1940Ping):
        startingPoints.append(pingRingPos)

# Set up plot
fig = plt.figure(1, figsize=(8.5, 11))
ax = plt.subplot(111, aspect='equal')
ax.set_xlim(60,115)
ax.set_ylim(-40,50)
#ax.set_xlim(80,120)
#ax.set_ylim(-40,20)

# Circle for 19:40 ping circle - 29.5 radius
pingCircle = Circle((satelliteInfo1940['LatLon'][1],satelliteInfo1940['LatLon'][0]), radius=29.5, fill=False)
ax.add_artist(pingCircle)

if filterUsingDoppler:
    dopplerError = "%d%%" % (dopplerDiffError * 100.0)
else:
    dopplerError = filterUsingDoppler
ax.set_title("MH370 Forwardtrack - %dkt - Doppler Filter - %s" % (aircraftGroundSpeed, dopplerError))

# Satellite positions
for satelliteInfo in satelliteInfos:
    ax.scatter(satelliteInfo['LatLon'][1], satelliteInfo['LatLon'][0])

# Render all possible starting positions
for pos in startingPoints:
    ax.scatter(pos[1], pos[0])

# Iterate over the starting points 
for pos in startingPoints:
    for bearing in range(0, 359, bearingIncrement):
    #for bearing in range(90, 270, 1):
        segments = [pos]
        lastPos = pos
        for index in range(0, len(satelliteInfos)-1):
            pingInterval = satelliteInfos[index]['NextPingTimeOffset']
            newPos = Geo.greatCircleDestination(lastPos, bearing, Geo.nmToKm((pingInterval/60.0)*aircraftGroundSpeed))
            satelliteRange = Geo.greatCircleDistance(newPos, satelliteInfos[index+1]['LatLon'])
            if math.fabs(satelliteRange - satelliteInfos[index+1]['PingRadius']) < pingRingDiffError * satelliteInfos[index+1]['PingRadius']:
                if filterUsingDoppler:
                    aircraftECEF = Geo.sphericalToECEF(newPos)
                    aircraftECEFVel = Geo.ecefVelocities(newPos, Geo.knotsToKms(aircraftGroundSpeed), bearing)
                    LOSSpeed = Geo.LOSSpeed(satelliteInfos[index+1]['XYZ'], satelliteInfos[index+1]['Velocity'], aircraftECEF, aircraftECEFVel) * -1.0
                    if math.fabs(LOSSpeed - satelliteInfos[index+1]['LOSSpeed']) < math.fabs(dopplerDiffError * satelliteInfos[index+1]['LOSSpeed']):
                        segments.append(newPos)
                        lastPos = newPos
                    else:
                        break
                else:
                    segments.append(newPos)
                    lastPos = newPos
            else:
                break
        if len(segments) == 5:
            for index in range(1, len(satelliteInfos)):
                segmentPos = segments[index]
                ax.scatter(segmentPos[1], segmentPos[0], c=satelliteInfos[index]['Color'])
                prevSegmentPos = segments[index-1]
                ax.plot([prevSegmentPos[1], segmentPos[1]], [prevSegmentPos[0], segmentPos[0]])

# Last radar position lat - 6.5381 lon - 96.408
ax.scatter(lastAircraftRadarPos[1], lastAircraftRadarPos[0], c='y', s=50, marker='D')
ax.annotate('Last radar position', xy=(lastAircraftRadarPos[1], lastAircraftRadarPos[0]), xytext=(lastAircraftRadarPos[1]+5, lastAircraftRadarPos[0]+5), arrowprops=dict(facecolor='black'))

if filterUsingDoppler:
    dopplerError = "%d" % (dopplerDiffError * 100.0)
else:
    dopplerError = filterUsingDoppler

plt.savefig("MH370 Forwardtrack - %dkt - Doppler Filter - %s.png" % (aircraftGroundSpeed, dopplerError))

plt.show()



