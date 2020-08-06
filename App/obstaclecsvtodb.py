from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker
import sys
import csv
import os
import pathlib
from os.path import join, isfile

root = sys.argv[1]
obstacle_path = root + '/CSV/'

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

def CSVToDB(icao, csv_path):
    csvReader = csv.reader(open(csv_path), delimiter=',')
    next(csvReader)
    for row in csvReader:
        print(type(row), len(row), csv_path)
        element = Obstacles(icao, row)
        InsertIfNotPresent(element)

def main():

    files = [f for f in os.listdir(
        obstacle_path) if os.path.isfile(join(obstacle_path, f))]
    for obstacle_file in files:
        icao: str = pathlib.Path(obstacle_file).stem
        obstacle_file = obstacle_path + '/' + obstacle_file
        CSVToDB(icao, obstacle_file)
    session.commit()


if __name__ == '__main__':
    main()
