import subprocess
import sys
import pathlib

if len(sys.argv) != 3 :
    print('Usage is automate.py APP_DIR DATA_DIR')
    quit(0)
# Get the App Location
apps: str = sys.argv[1]
# Get the Root Location for Data Storage
data_loc: str = sys.argv[2]

# Create the Given Folder if it does not exist
pathlib.Path(data_loc).mkdir(parents=True, exist_ok=True) 

# First Run PDFDownloader
def RunCSharpProjectWithDotNetRun(project_path: str):
    # Pass Required Arguments to DotNet
    completed = subprocess.run([
       'dotnet','run', # Name of App with Command
        '--configuration', 'Debug', #Start in Release Configuration
        '--project', # Specify That We are to Run project
        project_path, # Specify Project Path
        data_loc # Specify Command Line Path where to Perform Action
    ], shell=True # Ensure it can access current CMD path
    )
    return completed

def RunPythonScript(script_path: str):
    # Pass Required Argument to Python
    completed = subprocess.run([
       'python',
        script_path, # Specify Project Path
        data_loc # Specify Command Line Path where to Perform Action
    ], shell=True # Ensure it can access current CMD path
    )
    return completed
# Download All PDFs
def PDFDownloader():
    project_path: str = apps + '/' + 'PdfDownloader/PdfDownloader/PdfDownloader.csproj ' 
    return RunCSharpProjectWithDotNetRun(project_path)
# Download All PDFs
def ICAOCodeParser():
    project_path: str = apps + '/' + 'ICAOCodeParser/ICAOCodeParser/ICAOCodeParser.csproj ' 
    return RunCSharpProjectWithDotNetRun(project_path)
# Convert PDF to CSV
def PdfToCSVParser():
    project_path: str = apps + '/' + 'PdfToCSVParser/PdfToCSVParser/PdfToCSVParser.csproj'
    return RunCSharpProjectWithDotNetRun(project_path)
# Convert CSV To KML2D
def CSVToKML2D():
    script_path: str = apps + '/' + 'csv_kml_2d.py'
    return RunPythonScript(script_path)
# Convert CSV To KMZ
def CSVToKMZ():
    script_path: str = apps + '/' + 'csv_kmz.py'
    return RunPythonScript(script_path)

def GenerateNetworkLink():
    script_path: str = apps + '/' + 'network_link.py'
    return RunPythonScript(script_path)

def ICAOCSVToDb():
    script_path: str = apps + '/' + 'icaocsv2db.py'
    return RunPythonScript(script_path)
def ObstacleCSVToDb():
    script_path: str = apps + '/' + 'obstaclecsvtodb.py'
    return RunPythonScript(script_path)


# Push to Git
def PushToGit():
    script_path: str = apps + '/' + 'gitscript.py'
    return RunPythonScript(script_path)

# Run the Given Functions
ICAOCodeParser()
PDFDownloader()
PdfToCSVParser()
CSVToKML2D()
CSVToKMZ()
GenerateNetworkLink()
ICAOCSVToDb()
ObstacleCSVToDb()
#PushToGit()
