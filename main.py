import pathlib
import xml.dom.minidom
import sys
from os import listdir, getcwd
from os.path import join, isfile
import csv
from math import radians, cos, sin, asin, sqrt, tan
import geopy
from geopy.distance import VincentyDistance

root = sys.argv[1]
obs_csv_dir = root + '/CSV/'
kml_dir = root + '/KML/'
runway_csv_dir = root + '/CSVCentre/'

# given: lat1, lon1, b = bearing in degrees, d = distance in kilometers
def geodesic(lat1, lon1, d, b, el=0):
        origin = geopy.Point(lat1, lon1)
        destination = VincentyDistance(meters=d).destination(origin, b)
        lat2, lon2 = destination.latitude, destination.longitude
        return [lon2, lat2, el]




def createOLS(kmlDoc, documentElement,  lat1, lon1, lat2, lon2, truBearing, width):
        IHradius = 2000
        IHelevation = 150
        conicalSlope = 5/100
        conicalHeight = 35
        transitionalSlope = 20/100
        approachFirstLength = 1600
        approachSlope = 5/100
        approachDiversion = 10/100
        inner = []

        runway = list()
        runway.append(geodesic(lat1, lon1, width/2, truBearing+90, 0))
        runway.append(geodesic(lat1, lon1, width/2, truBearing-90, 0))
        runway.append(geodesic(lat2, lon2, width/2, truBearing-90, 0))
        runway.append(geodesic(lat2, lon2, width/2, truBearing+90, 0))
        runwayPolygon = createPolygon(kmlDoc, runway , inner, 'relativeToGround')

        innerHorizontalPolygon = createCircle(kmlDoc, (lat1+lat2)/2, (lon1+lon2)/2, IHradius, IHelevation, 0, 360)

        conicalPolygon = createPolygon( kmlDoc,
                                        getCircle(kmlDoc, (lat1+lat2)/2, (lon1+lon2)/2, IHradius, IHelevation, 0, 360),
                                        getCircle(kmlDoc, (lat1+lat2)/2, (lon1+lon2)/2, conicalHeight/tan(conicalSlope), IHelevation+conicalHeight, 0, 360),
                                        'relativeToGround'
                                      )

        transitional1 = list()
        transitional1.append(geodesic(lat1, lon1, width/2, truBearing+90, 0))
        transitional1.append(geodesic(lat1, lon1, width/2 + conicalHeight/tan(transitionalSlope), truBearing+90, conicalHeight))
        transitional1.append(geodesic(lat2, lon2, width/2 + conicalHeight/tan(transitionalSlope), truBearing+90, conicalHeight))
        transitional1.append(geodesic(lat2, lon2, width/2, truBearing+90, 0))
        transitionalPolygon1 = createPolygon(kmlDoc, transitional1, inner, 'relativeToGround')

        transitional2 = list()
        transitional2.append(geodesic(lat1, lon1, width/2, truBearing-90, 0))
        transitional2.append(geodesic(lat1, lon1, width/2 + conicalHeight/tan(transitionalSlope), truBearing-90, conicalHeight))
        transitional2.append(geodesic(lat2, lon2, width/2 + conicalHeight/tan(transitionalSlope), truBearing-90, conicalHeight))
        transitional2.append(geodesic(lat2, lon2, width/2, truBearing-90, 0))
        transitionalPolygon2 = createPolygon(kmlDoc, transitional2, inner, 'relativeToGround')        

        approachFirst = list()
        approachFirst.append(geodesic(lat1, lon1, width/2, truBearing-90, 0))
        approachFirst.append(geodesic(lat1, lon1, width/2, truBearing+90, 0))
        approachFirst.append(geodesic(lat1, lon1, width/2 + 160.5354 , truBearing-90, 80.066))
        approachFirst.append(geodesic(lat1, lon1, width/2 + 160.5354 , truBearing-90, 80.066))
        approachFirstPolygon = createPolygon(kmlDoc, approachFirst, inner, 'relativeToGround')  

        placemark1 = kmlDoc.createElement('Placemark')
        placemark2 = kmlDoc.createElement('Placemark')
        placemark3 = kmlDoc.createElement('Placemark')
        placemark4 = kmlDoc.createElement('Placemark')
        placemark5 = kmlDoc.createElement('Placemark')
        placemark6 = kmlDoc.createElement('Placemark')
        
        placemark1.appendChild(runwayPolygon)
        styleUrlElement1 = kmlDoc.createElement('styleUrl')
        placemark1.appendChild(styleUrlElement1)
        styleUrlElement1.appendChild(kmlDoc.createTextNode('#30transYellow'))

        placemark2.appendChild(innerHorizontalPolygon)
        styleUrlElement2 = kmlDoc.createElement('styleUrl')
        placemark2.appendChild(styleUrlElement2)
        styleUrlElement2.appendChild(kmlDoc.createTextNode('#16transBlue'))

        placemark3.appendChild(conicalPolygon)
        styleUrlElement3 = kmlDoc.createElement('styleUrl')
        placemark3.appendChild(styleUrlElement3)
        styleUrlElement3.appendChild(kmlDoc.createTextNode('#16transBlue'))

        placemark4.appendChild(transitionalPolygon1)
        styleUrlElement4 = kmlDoc.createElement('styleUrl')
        placemark4.appendChild(styleUrlElement4)
        styleUrlElement4.appendChild(kmlDoc.createTextNode('#100transRed'))

        placemark5.appendChild(transitionalPolygon2)
        styleUrlElement5 = kmlDoc.createElement('styleUrl')
        placemark5.appendChild(styleUrlElement5)
        styleUrlElement5.appendChild(kmlDoc.createTextNode('#100transRed'))

        placemark6.appendChild(approachFirstPolygon)
        styleUrlElement6 = kmlDoc.createElement('styleUrl')
        placemark6.appendChild(styleUrlElement1)
        styleUrlElement6.appendChild(kmlDoc.createTextNode('#30transYellow'))

        documentElement.appendChild(placemark1)
        documentElement.appendChild(placemark2)
        documentElement.appendChild(placemark3)
        documentElement.appendChild(placemark4)
        documentElement.appendChild(placemark5)

        


def getCircle(kmlDoc, lat1, long1, radius, elevation, bearing1, bearing2):
        points = list()
        deviation = 0.001
        bearing = bearing1
        while(bearing <= bearing2):
                points.append(geodesic(lat1, long1, radius, bearing ,elevation))
                # points.append(elevation)
                bearing+= 1
        return points


def createCircle(kmlDoc, lat1, long1, radius, elevation, bearing1, bearing2):
        empty =[]
        points = getCircle(kmlDoc, lat1, long1, radius, elevation, bearing1, bearing2)
        PolygonElement = createPolygon(kmlDoc, points ,empty,'relativeToGround')
        return PolygonElement


def createStyle(kmlDoc, documentElement, id_name, color):
    styleElement = kmlDoc.createElement('Style')
    PolystyleElement = kmlDoc.createElement('PolyStyle')
    colorElement = kmlDoc.createElement('color')
    documentElement.appendChild(styleElement)
    styleElement.appendChild(PolystyleElement)
    PolystyleElement.appendChild(colorElement)
    styleElement.setAttribute('id', id_name)
    colorElement.appendChild(kmlDoc.createTextNode(color))

def createKML(fileName, obsCsvReader, runwayCsvReader):
    # This constructs the KML document from the CSV file.
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
    kmlElement.setAttribute('xmlns','http://earth.google.com/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    kmlElement.appendChild(documentElement)
    createStyle(kmlDoc, documentElement, 'opaqueRED', 'ff0000cc')
    createStyle(kmlDoc, documentElement, '16transBlue', '10ff0000')
    createStyle(kmlDoc, documentElement, '100transRed', 'ff00cc00')
    createStyle(kmlDoc, documentElement, '30transYellow', '20ffff00')
    createStyle(kmlDoc, documentElement, 'Purple', 'ffff00ff')

    next(obsCsvReader)


    for row in obsCsvReader:
        placemarkElement = createPlacemark(kmlDoc, row)
        documentElement.appendChild(placemarkElement)

    next(runwayCsvReader)
    datalist = list()
    for row in runwayCsvReader:
        datalist.append(row[0])
        datalist.append(row[1])
        datalist.append(row[2])
        datalist.append(row[3])
    if len(datalist) > 5:
        createOLS(kmlDoc, documentElement, float(datalist[0]), float(datalist[1]), float(datalist[4]), float(datalist[5]), float(datalist[3]), float(datalist[2]))
    kmlFile = open(fileName, 'wb')
    kmlFile.write(kmlDoc.toprettyxml('  ', newl = '\n', encoding = 'utf-8'))

    return kmlFile


def createPlacemark(kmlDoc, row):
    placemark = kmlDoc.createElement('Placemark')
    name = kmlDoc.createElement('name')
    description = kmlDoc.createElement('description')
    point = kmlDoc.createElement('Point')
    coordinate =kmlDoc.createElement('coordinates')
    styleUrl = kmlDoc.createElement('styleUrl')

    placemark.appendChild(name)
    placemark.appendChild(description)
    placemark.appendChild(point)
    point.appendChild(coordinate)
    placemark.appendChild(styleUrl)

    polygonElement = createObstacle(kmlDoc , float(row[2]), float(row[3]), float(row[4]))
    placemark.appendChild(polygonElement)

    des_string = '<div>' + row[6]  + '</div>' + '<div>' + 'Runway: ' + row[0]  + '</div>'  +'<div>' + 'Elevation (in ft): ' + row[4]  + '</div>' +'<div>' + 'Marking: ' + row[5]  + '</div>' 
    name.appendChild(kmlDoc.createTextNode(row[6]))
    description.appendChild(kmlDoc.createTextNode(des_string))
    coordinate.appendChild(kmlDoc.createTextNode(row[3] + ',' + row[2]))
    styleUrl.appendChild(kmlDoc.createTextNode('#opaqueRED'))
    
    return placemark

def createPolygon(kmlDoc, OuterPoints, InnerPoints, altmode):
        OuterPoints.append(OuterPoints[0])
        strOuterPoint = ''

        for OuterPoint in OuterPoints:
                 
                for coordinate in OuterPoint:
                        strOuterPoint += str(coordinate) + ','
                strOuterPoint = strOuterPoint[:-1]
                strOuterPoint += '\n'

        if (len(InnerPoints) !=0):
                InnerPoints.append(InnerPoints[0])
        strInnerPoint = ''
        for InnerPoint in InnerPoints:
                for coordinate in InnerPoint:
                        strInnerPoint += str(coordinate) + ','
                strInnerPoint = strInnerPoint[:-1]
                strInnerPoint += '\n'

        PolygonElement = kmlDoc.createElement('Polygon')
        extrudeElement = kmlDoc.createElement('extrude')
        altModeElement = kmlDoc.createElement('altitudeMode')
        PolygonElement.appendChild(extrudeElement)
        PolygonElement.appendChild(altModeElement)

        outerBoundElement = kmlDoc.createElement('outerBoundaryIs')
        outerBoundLinearRingElement = kmlDoc.createElement('LinearRing')
        outerBoundCoordinateElement = kmlDoc.createElement('coordinates')
        PolygonElement.appendChild(outerBoundElement)
        outerBoundElement.appendChild(outerBoundLinearRingElement)
        outerBoundLinearRingElement.appendChild(outerBoundCoordinateElement)
        
        innerBoundElement = kmlDoc.createElement('innerBoundaryIs')
        innerBoundLinearRingElement = kmlDoc.createElement('LinearRing')
        innerBoundCoordinateElement = kmlDoc.createElement('coordinates')
        PolygonElement.appendChild(innerBoundElement)
        innerBoundElement.appendChild(innerBoundLinearRingElement)
        innerBoundLinearRingElement.appendChild(innerBoundCoordinateElement)        
        
        extrudeElement.appendChild(kmlDoc.createTextNode('1'))
        altModeElement.appendChild(kmlDoc.createTextNode(altmode))
        innerBoundCoordinateElement.appendChild(kmlDoc.createTextNode(strInnerPoint))
        outerBoundCoordinateElement.appendChild(kmlDoc.createTextNode(strOuterPoint))

        return PolygonElement

def createObstacle(kmlDoc, latitude, longitude ,elevation):
        elevation/=3.281
        a = 0.0001
        point1 = (longitude , latitude + a , elevation)
        point2 = (longitude , latitude - a , elevation)
        point3 = (longitude + a, latitude , elevation)
        point4 = (longitude - a, latitude , elevation)

        points1 = [point1 , point3 , point2 , point4]
        points2 = []
        

        return createPolygon(kmlDoc , points1 , points2, 'absolute')


def main():

    #root = sys.argv[1]
    #obs_csv_dir = root + '/CSV/'
    #kml_dir = root + '/KML/'
    pathlib.Path(kml_dir).mkdir(parents=True, exist_ok=True) 

    files = [f for f in listdir(obs_csv_dir) if isfile(join(obs_csv_dir, f))]

    icaos = []
    for csv_file in files:
            icaos.append(csv_file[:-4])
    
    for icao in icaos:
        file_name = icao.upper()
        obs_csv_file = obs_csv_dir + '/' + file_name + '.CSV'
        runway_csv_file = runway_csv_dir + file_name + '.CSV'
        kml_file = kml_dir + '/' + file_name + '.KML'
        print(kml_file)
        obCsvReader = csv.reader(open(obs_csv_file), delimiter = ',')
        runwayCsvReader = csv.reader(open(runway_csv_file), delimiter = ',')
        kml = createKML(kml_file, obCsvReader, runwayCsvReader)


if __name__ == '__main__':
  main()
