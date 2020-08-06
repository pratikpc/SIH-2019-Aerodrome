import csv
import pathlib
import xml.dom.minidom
import sys
import shutil

from os import listdir, getcwd
from os.path import join, isfile
from distutils.dir_util import copy_tree

# Get the Root Directory
root = sys.argv[1] 
csvFolder = root + '/CSV/'
kmzTmpFolder = root + '/KMZTemp/'
daeFolder = root + '/dae/'
kmzFinalFolder = root + '/KMZ/'
scaling_factor = 0.01157

def createKML(csvFile, fileName, icaoAirport):
    csvReader = csv.reader(open(csvFile), delimiter = ',')
    # This constructs the KML document from the CSV file.
    kmlDoc = xml.dom.minidom.Document()
#below code creates a basic structure of how the docs will look 
    kmlElement = kmlDoc.createElementNS('http://www.opengis.net/kml/2.2', 'kml')
    kmlElement.setAttribute('xmlns','http://www.opengis.net/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)

    # Ignore the Header Values
    next(csvReader)

    # Store List of DAE Models to Add
    # List is Unique to Reduce Duplication of Effort
    daeAdd = set()
#create the placematk sectiin and append it to the document tag
    for row in csvReader:
        placemarkElement = createPlacemark(kmlDoc, row, icaoAirport)
        documentElement.appendChild(placemarkElement)
        daeAdd.add(row[1].upper()) # Add the Type of Obstacle. We use this to detect DAE
    kmlFile = open(fileName, 'wb') #writes the .kml file in byte mode
    kmlFile.write(kmlDoc.toprettyxml('  ', newl = '\n', encoding = 'utf-8'))
    
    # Folder to Store DAE in KMZTemp
    daeKMZTmpDir = kmzTmpFolder + icaoAirport + '/dae';

    # Copy the Required DAE Files and Contents
    for daeName in daeAdd:
        src = daeFolder  + '/red'
        
        dest = daeKMZTmpDir +  '/red'
        copy_tree(src, dest)
	
def createPlacemark(kmlDoc, row, icaoAirport):
    placemark = kmlDoc.createElement('Placemark')
    extended = kmlDoc.createElement('ExtendedData')
    name = kmlDoc.createElement('name')
    runway = kmlDoc.createElement('Data')
    obs_type = kmlDoc.createElement('Data')
    marking = kmlDoc.createElement('Data')
    remark = kmlDoc.createElement('Data')
    elevation = kmlDoc.createElement('Data')
    runway_value = kmlDoc.createElement('value')
    obs_type_value = kmlDoc.createElement('value')
    marking_value = kmlDoc.createElement('value')
    remark_value = kmlDoc.createElement('value')
    elevation_value = kmlDoc.createElement('value')
    model = kmlDoc.createElement('Model')
    altitude_mode = kmlDoc.createElement('altitudeMode')
    location = kmlDoc.createElement('Location')
    longitude = kmlDoc.createElement('longitude')
    latitude = kmlDoc.createElement('latitude')
    altitude = kmlDoc.createElement('altitude')
    orientation = kmlDoc.createElement('Orientation')
    heading = kmlDoc.createElement('heading')
    tilt = kmlDoc.createElement('tilt')
    roll = kmlDoc.createElement('roll')
    scale = kmlDoc.createElement('Scale')
    x = kmlDoc.createElement('x')
    y = kmlDoc.createElement('y')
    z = kmlDoc.createElement('z')
    link = kmlDoc.createElement('Link')
    href = kmlDoc.createElement('href')
#above block of codecreates all the tags required for the project more can be added
    placemark.appendChild(name)
    placemark.appendChild(extended)
    placemark.appendChild(model)
#append the tags according to parent child relation
    extended.appendChild(runway)
    extended.appendChild(obs_type)
    extended.appendChild(marking)
    extended.appendChild(remark)
    extended.appendChild(elevation)


    runway.appendChild(runway_value)
    obs_type.appendChild(obs_type_value)
    marking.appendChild(marking_value)
    remark.appendChild(remark_value)
    elevation.appendChild(elevation_value)

    model.appendChild(altitude_mode)
    model.appendChild(location)
    model.appendChild(orientation)
    model.appendChild(scale)
    model.appendChild(link)

    location.appendChild(longitude)
    location.appendChild(latitude)
    location.appendChild(altitude)

    orientation.appendChild(heading)
    orientation.appendChild(tilt)
    orientation.appendChild(roll)

    scale.appendChild(x)
    scale.appendChild(y)
    scale.appendChild(z)

    link.appendChild(href)

#this piece of code does this <data name="">
    runway.setAttribute('name', '  Runway  ')
    obs_type.setAttribute('name', '  Obstacle Type  ')
    marking.setAttribute('name', '  Marking  ')
    remark.setAttribute('name', '  Remark  ')
    elevation.setAttribute('name' , '  Elevation  ')

    height = float(row[4]) * scaling_factor
    height = str(height)
    

    #text nodes are basically what values you write in your enclosing tags


    runway_value.appendChild(kmlDoc.createTextNode(row[0]))
    obs_type_value.appendChild(kmlDoc.createTextNode(row[1]))
    marking_value.appendChild(kmlDoc.createTextNode(row[5]))
    remark_value.appendChild(kmlDoc.createTextNode(row[6]))
    elevation_value.appendChild(kmlDoc.createTextNode(row[4] + ' ft'))
    latitude.appendChild(kmlDoc.createTextNode(row[2]))
    longitude.appendChild(kmlDoc.createTextNode(row[3]))
    altitude.appendChild(kmlDoc.createTextNode('0'))
    heading.appendChild(kmlDoc.createTextNode('0'))
    tilt.appendChild(kmlDoc.createTextNode('0'))
    roll.appendChild(kmlDoc.createTextNode('0'))
    x.appendChild(kmlDoc.createTextNode('0.5'))
    y.appendChild(kmlDoc.createTextNode('0.5'))
    z.appendChild(kmlDoc.createTextNode(height))
    altitude_mode.appendChild(kmlDoc.createTextNode('clampToSeaFloor'))
    name.appendChild(kmlDoc.createTextNode(row[6]))

    dae_path = 'dae' + '/red/Untitled.dae' # Find Relative Path
    href.appendChild(kmlDoc.createTextNode(dae_path))
#link to the 3d models
    return placemark
#placemark is returned to become the child of document

def main():
    files = [f for f in listdir(csvFolder) if isfile(join(csvFolder, f))]
    # Remove Previous Generation of Code in TMP Folder
    shutil.rmtree(kmzTmpFolder,True);
    for csv_file in files:
        print('Started Parsing ', csv_file)
        icaoAirport = pathlib.Path(csv_file).stem # Extract VAAH from VAAH.csv
        csvFile = csvFolder + icaoAirport + '.CSV'
        # Create Path to KMZ File
        kmzAirportPath = kmzTmpFolder + icaoAirport + '/'
        # Create the Given Folder if it does not exist
        pathlib.Path(kmzAirportPath).mkdir(parents=True, exist_ok=True) 
	    # doc.KML is the destination KML
        createKML(csvFile, kmzAirportPath + icaoAirport + '.kml', icaoAirport)

        # As the KMZTmp now has Directory Structure for KMZ for the given airport
        # We can Add it to ZIP and Rename ZIP to KMZ and be done with it
        shutil.make_archive(kmzFinalFolder + icaoAirport, 'zip', kmzAirportPath)
        zip_name = kmzFinalFolder + icaoAirport + '.zip'
        kmz_name = kmzFinalFolder + icaoAirport + '.KMZ'
        shutil.move(zip_name, kmz_name)
        print('Finished ', kmz_name)

    
    # Remove TMP Folder When Unrequired
    shutil.rmtree(kmzTmpFolder,True);

if __name__ == '__main__':
  main()