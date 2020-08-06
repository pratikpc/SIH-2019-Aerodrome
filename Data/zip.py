
import zipfile
from os import listdir, getcwd
from os.path import join, isfile,relpath
import shutil

 
files = [f for f in listdir('D:/Desktop/laerodrome/Data/KML/') if isfile(join('D:/Desktop/laerodrome/Data/KML/', f))]
 
for file in files:
    print(file)
    data = file[:-4]
    data1 = file[4:]
    print(data1)
    if data1 == '.KML':
        zip_path = 'D:/Desktop/laerodrome/Data/KML/'+ data + '.zip'
        print(zip_path)
        fantasy_zip = zipfile.ZipFile(zip_path, 'w')
        fantasy_zip.write(join('D:/Desktop/laerodrome/Data/KML/', file), relpath(join('D:/Desktop/laerodrome/Data/KML/',file), 'D:/Desktop/laerodrome/Data/KML'), compress_type = zipfile.ZIP_DEFLATED)
        fantasy_zip.close()


files = [f for f in listdir('D:/Desktop/laerodrome/Data/KML/') if isfile(join('D:/Desktop/laerodrome/Data/KML/', f))]
for file in files:
    print(file)
    data = file[:-4]
    data1 = file[4:]
    if data1 == '.zip':
        zip_name =  data + '.zip'
        kmz_name =  data + '.KMZ'
        shutil.move(zip_name, kmz_name)