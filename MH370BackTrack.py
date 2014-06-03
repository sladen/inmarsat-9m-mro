import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

satelliteInfo0011 = { 'Y': 0.0,             'Vz': 159.58,  'LOSSpeed': 250.43, 'PreviousPingTimeOffset': 91.0, 'PingRadius': 2652, 'Color': 'b', 'Elevation': 39.33 }
satelliteInfo2240 = { 'Y': 233.91 - 451.20, 'Vz': 123.31,  'LOSSpeed': 175.49, 'PreviousPingTimeOffset': 60.0, 'PingRadius': 2206, 'Color': 'r', 'Elevation': 47.54 }
satelliteInfo2140 = { 'Y': 233.91 - 557.62, 'Vz':  88.38,  'LOSSpeed': 118.34, 'PreviousPingTimeOffset': 60.0, 'PingRadius': 1965, 'Color': 'g', 'Elevation': 52.01 }
satelliteInfo2040 = { 'Y': 233.91 - 625.88, 'Vz':  47.42,  'LOSSpeed':  57.02, 'PreviousPingTimeOffset': 60.0, 'PingRadius': 1806, 'Color': 'c', 'Elevation': 54.98 }
satelliteInfo1940 = { 'Y': 233.91 - 651.30, 'Vz':   3.22,  'LOSSpeed':   4.97, 'PreviousPingTimeOffset': 78.0, 'PingRadius': 1760, 'Color': 'm', 'Elevation': 55.80 }

satelliteInfos = [satelliteInfo0011,  satelliteInfo2240, satelliteInfo2140, satelliteInfo2040, satelliteInfo1940] 

LOSSpeeds = [ (250.43, 125.35), (175.49, 100.64), (118.34, 79.85), (57.02, 65.80), (4.97, 39.14) ]

aircraftGS = 500

# Setup LOS Speeds
LOSSpeedsSelection = 1
for index in range(0, len(satelliteInfos)):
    first, second = LOSSpeeds[index]
    if LOSSpeedsSelection == 1:
        satelliteInfos[index]['LOSSpeed'] = first
    else:
        satelliteInfos[index]['LOSSpeed'] = second

# Set up plot
fig = plt.figure(1, figsize=(8.5, 11))
ax = plt.subplot(111, aspect='equal')
#ax.set_xlim(-3000,3000)
#ax.set_ylim(3000,-3000)
ax.set_xlim(-200,3000)
ax.set_ylim(3000,-1500)

for satelliteInfo in satelliteInfos:
    pingCircle = Circle((0,satelliteInfo['Y']), radius=satelliteInfo['PingRadius'], fill=False)
    ax.add_artist(pingCircle)
    ax.scatter(0, satelliteInfo['Y'], c=satelliteInfo['Color'])

ax.set_title("MH370 Backtrack - %dkt - Last Doppler LOS Speed - %dkt" % (aircraftGS, satelliteInfos[0]['LOSSpeed']))

ax.text(0, 2800, '00:11')
ax.text(0, 2150, '22:40')
ax.text(0, 1800, '21:40')
ax.text(0, 1550, '20:40')
ax.text(0, 1300, '19:40')

# Last radar position lat - 6.5381 lon - 96.408
ax.scatter(1906.59, -354.75, c='y', s=50, marker='D')
aircraftCircle = Circle((1906.59,-354.75), radius=650, fill=False, color='y')
ax.add_artist(aircraftCircle)
ax.annotate('Northern 19:40 Arc', xy=(1668,-958), xytext=(700,-1100), arrowprops=dict(facecolor='black'))
ax.annotate('Southern 19:40 Arc', xy=(1634,235),  xytext=(600,100),   arrowprops=dict(facecolor='black'))

latitudes = [(35, ' '), (333, 'S5'), (632, 'S10'), (931, 'S15'), (1223, 'S20'), (1528, 'S25'), (1828, 'S30'), (2127, 'S35'), (-263, 'N5'), (-562, 'N10'), (-861, 'N15')]

for latitude in latitudes:
    yCart, latText = latitude
    ax.plot((-3000,3000), (yCart,yCart), color='grey', alpha=0.5)
    ax.text(2750, yCart, latText)

def distance(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx * dx + dy * dy)

def calc(aircraftX, aircraftY, satelliteIndex):
    if satelliteIndex == len(satelliteInfos) - 1:
        return

    # Unpack satellite info
    satelliteInfo = satelliteInfos[satelliteIndex]
    satelliteVz = satelliteInfo['Vz']
    satelliteElevation = satelliteInfo['Elevation']
    satelliteY = satelliteInfo['Y']
    LOSSpeed = satelliteInfo['LOSSpeed']
    backtrackTime = satelliteInfo['PreviousPingTimeOffset']
    
    distanceFromSatelliteToAircraft = distance(0.0, satelliteY, aircraftX, aircraftY)
    bearingFromSatelliteToAircaft = math.asin(aircraftX/distanceFromSatelliteToAircraft)

    aircraftDistanceCoveredBetweenLastTwoPings = (backtrackTime / 60.0) * aircraftGS

    satelliteCone = satelliteVz * math.cos(math.radians(satelliteElevation))
    aircraftCone = aircraftGS * math.cos(math.radians(satelliteElevation))

    satelliteLOS = satelliteCone * math.cos(bearingFromSatelliteToAircaft)

    try:
        aircraftBearingAngleDifference = math.degrees(math.acos((LOSSpeed + satelliteLOS) / aircraftCone))
    except ValueError:
        return

    aircraftLOS = aircraftCone * math.cos(math.radians(aircraftBearingAngleDifference))

    finalLOS = aircraftLOS - satelliteLOS

    bearingPositive = 180 - math.degrees(bearingFromSatelliteToAircaft) + aircraftBearingAngleDifference
    bearingNegative = 180 - math.degrees(bearingFromSatelliteToAircaft) - aircraftBearingAngleDifference

    matches = []

    for bearing in [bearingPositive, bearingNegative]:
        previousAircraftX = -9999
        previousAircraftY = -9999
        if bearing > 90.0 and bearing <= 180.0:
            previousAircraftX = aircraftX - aircraftDistanceCoveredBetweenLastTwoPings * math.sin(math.radians(180.0 - bearing))
            previousAircraftY = aircraftY - aircraftDistanceCoveredBetweenLastTwoPings * math.cos(math.radians(180.0 - bearing))
        elif bearing > 180.0 and bearing <= 270.0:
            previousAircraftX = aircraftX + aircraftDistanceCoveredBetweenLastTwoPings * math.sin(math.radians(bearing - 180.0))
            previousAircraftY = aircraftY - aircraftDistanceCoveredBetweenLastTwoPings * math.cos(math.radians(bearing - 180.0))
        if previousAircraftX != -9999 and previousAircraftY != -9999:
            distanceFromPreviousSatelitePoint = distance(0.0, satelliteInfos[satelliteIndex + 1]['Y'], previousAircraftX, previousAircraftY)
            rangeRingDiff = math.fabs(distanceFromPreviousSatelitePoint - satelliteInfos[satelliteIndex + 1]['PingRadius'])
            if rangeRingDiff < (0.02 + (satelliteIndex * 0.5)/100.0) * satelliteInfos[satelliteIndex + 1]['PingRadius']:
                if satelliteIndex == 0:
                    ax.scatter(aircraftX, aircraftY, c=satelliteInfo['Color'])
                ax.scatter(previousAircraftX, previousAircraftY, c=satelliteInfos[satelliteIndex + 1]['Color'])
                ax.plot([aircraftX, previousAircraftX], [aircraftY, previousAircraftY])
                calc(previousAircraftX, previousAircraftY, satelliteIndex + 1)

    return

for bearing in range(1, 89, 1):
    pingRadius = satelliteInfos[0]['PingRadius']
    aircraftX = pingRadius * math.sin(math.radians(bearing))
    aircraftY = pingRadius * math.cos(math.radians(bearing))
    calc(aircraftX, aircraftY, 0)

plt.savefig("MH370 Backtrack - %dkt - Last Doppler LOS Speed - %dkt.png" % (aircraftGS, satelliteInfos[0]['LOSSpeed']))

plt.show()
