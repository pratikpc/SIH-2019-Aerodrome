import pathlib
import xml.dom.minidom
import sys
from os import listdir, getcwd
from os.path import join, isfile
import csv
from math import radians, cos, sin, asin, sqrt


root = sys.argv[1]
csv_path = root + '/CSV/'
kml2D_path = root + '/KML2D/'


def createKML(csvReader, fileName):
    # This constructs the KML document from the CSV file.
    kmlDoc = xml.dom.minidom.Document()

    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
    kmlElement.setAttribute('xmlns','http://earth.google.com/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    styleElement = kmlDoc.createElement('Style')
    PolystyleElement = kmlDoc.createElement('PolyStyle')
    colorElement = kmlDoc.createElement('color')
    #cmElement = kmlDoc.createElement('colorMode')
    kmlElement.appendChild(documentElement)
    documentElement.appendChild(styleElement)
    styleElement.appendChild(PolystyleElement)
    PolystyleElement.appendChild(colorElement)
    #PolystyleElement.appendChild(cmElement)

    styleElement.setAttribute('id', 'exampleStyle')
    colorElement.appendChild(kmlDoc.createTextNode('ff0000cc'))


    next(csvReader)

    for row in csvReader:
        placemarkElement = createPlacemark(kmlDoc, row)
        documentElement.appendChild(placemarkElement)
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
    styleUrl.appendChild(kmlDoc.createTextNode('#exampleStyle'))
    
    return placemark

def createPolygon(kmlDoc, points):
        strPoint = ''

        for point in points:
                for coordinate in point:
                        strPoint += str(coordinate) + ','
                strPoint = strPoint[:-1]
                strPoint += '\n'

        PolygonElement = kmlDoc.createElement('Polygon')
        extrudeElement = kmlDoc.createElement('extrude')
        altModeElement = kmlDoc.createElement('altitudeMode')
        outerBoundElement = kmlDoc.createElement('outerBoundaryIs')
        LinearRingElement = kmlDoc.createElement('LinearRing')
        coordinateElement = kmlDoc.createElement('coordinates')
        
        #above block of codecreates all the tags required for the project more can be added
        PolygonElement.appendChild(extrudeElement)
        PolygonElement.appendChild(altModeElement)
        PolygonElement.appendChild(outerBoundElement)
        #append the tags according to parent child relation
        outerBoundElement.appendChild(LinearRingElement)
        LinearRingElement.appendChild(coordinateElement)

#text nodes are basically what values you write in your enclosing tags
        extrudeElement.appendChild(kmlDoc.createTextNode('1'))
        altModeElement.appendChild(kmlDoc.createTextNode('absolute'))
        coordinateElement.appendChild(kmlDoc.createTextNode(strPoint))
       
        return PolygonElement

def createObstacle(kmlDoc, latitude, longitude ,elevation):
        elevation/=3.281
        a = 0.0001
        point1 = (longitude , latitude + a , elevation)
        point2 = (longitude , latitude - a , elevation)
        point3 = (longitude + a, latitude , elevation)
        point4 = (longitude - a, latitude , elevation)

        points = (point1 , point3 , point2 , point4 , point1)
        

        return createPolygon(kmlDoc , points)


def main():
    files = [f for f in listdir(csv_path) if isfile(join(csv_path, f))]
    pathlib.Path(kml2D_path).mkdir(parents=True, exist_ok=True) 
    for csv_file in files:
        path = csv_path + '/' + csv_file
        kmlValue = csv_file[:-4]
        kmlpath = kml2D_path +'/' + kmlValue
        csvreader = csv.reader(open(path), delimiter = ',')
        kml = createKML(csvreader, kmlpath + '.KML')

if __name__ == '__main__':
  main()
