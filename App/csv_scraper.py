# import pathlib
# import xml.dom.minidom
# import sys
# from os import listdir, getcwd
# from os.path import join, isfile
# import csv


# csv_path = "XXXXXX"

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker
import sys
import csv
import os
import pathlib
from os.path import join, isfile

db_config = {'user': 'postgres', 'password': 'postgres',
             'netloc': 'localhost', 'port': '5432', 'dbname': 'aerodrome'}

def GenerateUri(db_config: map):
    return  'postgresql+psycopg2://' + db_config['user'] + ':' + db_config['password'] + '@' + db_config['netloc'] + ':' + db_config['port'] + '/' + db_config['dbname']

db = create_engine(GenerateUri(db_config))
base = declarative_base()


class Obstacles(base):
    __tablename__ = 'obstacles'
    obs_id = Column(Integer, primary_key=True)
    icao = Column(String)
    affected = Column(String)
    obs_type = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    elevation = Column(String)
    marking = Column(String)
    remark = Column(String)

    def __init__(self, icao, row: list):
        self.icao = icao
        self.affected = row[0]
        self.obs_type = row[1]
        self.latitude = row[2]
        self.longitude = row[3]
        self.elevation = row[4]
        self.marking = row[5]
        self.remark = row[6]


Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)

def InsertIfNotPresent(obstacle: Obstacles):
    if session.query(Obstacles)\
    .filter(Obstacles.affected == obstacle.affected)\
    .filter(Obstacles.elevation == obstacle.elevation)\
    .filter(Obstacles.icao == obstacle.icao)\
    .filter(Obstacles.latitude == obstacle.latitude)\
    .filter(Obstacles.longitude == obstacle.longitude)\
    .filter(Obstacles.marking == obstacle.marking)\
    .filter(Obstacles.remark == obstacle.remark)\
    .count() == 0:
        session.add(obstacle)

def IsFloat(text: str):
        try:
                x = float(text)
                return True
        except:
                return False

def CSVToDB(csv_path):
    csvReader = csv.reader(open(csv_path), delimiter=',')
 
    for row in csvReader:
        if len(row) < 9 or not (IsFloat(row[2]) and IsFloat(row[3]) and IsFloat(row[4])):
                continue
        uid = row[0]
        obs_type = row[1]
        latitude = str(float(row[2]) + float(row[3])/60 + float(row[4])/3600)
        longitude = str(float(row[5]) + float(row[6])/60 + float(row[7])/3600)
        elevation = row[8]
        remark = row[9]

        obstacle = [uid,obs_type,latitude,longitude,elevation,"NIL",remark]
        icao = uid[0:4].upper()
        element = Obstacles(icao, obstacle)
        InsertIfNotPresent(element)
        print(icao)


def main():
    obstacle_file = sys.argv[1]
    CSVToDB(obstacle_file)
    session.commit()


if __name__ == '__main__':
    main()
