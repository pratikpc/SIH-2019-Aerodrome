import xml.dom.minidom
import sys
from os import listdir, getcwd
from os.path import join, isfile
import pathlib

root = sys.argv[1]

kmz_path = root + '/KMZ/'
link_path =  root + '/NetworkLink/'
github_link = 'http://localhost:800/kmz'

# Create directory if not exists
pathlib.Path(link_path).mkdir(parents=True, exist_ok=True) 

files = [f for f in listdir(kmz_path) if isfile(join(kmz_path, f))]
for kmz in files:

    kmlDoc = xml.dom.minidom.Document()

    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
    kmlElement.setAttribute('xmlns' ,'http://www.opengis.net/kml/2.2' )
    kmlElement.setAttribute('xmlns:gx' ,'http://www.google.com/kml/ext/2.2' )
    kmlElement.setAttribute('xmlns:kml' ,'http://www.opengis.net/kml/2.2')
    kmlElement.setAttribute('xmlns:atom' ,'http://www.w3.org/2005/Atom')
    kmlElement = kmlDoc.appendChild(kmlElement)

    networkElement = kmlDoc.createElement('NetworkLink')
    openElement = kmlDoc.createElement('open')
    linkElement = kmlDoc.createElement('Link')
    hrefElement = kmlDoc.createElement('href')
    viewRefreshMode = kmlDoc.createElement('viewRefreshMode')
    flyElement = kmlDoc.createElement('flyToView')

    kmlElement.appendChild(networkElement)
    networkElement.appendChild(openElement)
    networkElement.appendChild(linkElement)
    networkElement.appendChild(flyElement)
    linkElement.appendChild(viewRefreshMode)
    linkElement.appendChild(hrefElement)

    github = github_link 
    github = github + kmz 
    openElement.appendChild(kmlDoc.createTextNode('1'))
    viewRefreshMode.appendChild(kmlDoc.createTextNode('onRequest'))
    hrefElement.appendChild(kmlDoc.createTextNode(github))
    flyElement.appendChild(kmlDoc.createTextNode('1'))

    kmz = kmz[:-4]
    filename = link_path + kmz + '.KML'
    kmlFile = open(filename, 'wb')
    kmlFile.write(kmlDoc.toprettyxml('  ', newl = '\n', encoding = 'utf-8'))