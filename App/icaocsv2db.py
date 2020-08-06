from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker
import sys
import csv
import os

root = sys.argv[1]
icao_path = root + '/' + 'ICAO.colonsv'

db_config = {'user': 'postgres', 'password': 'postgres',
             'netloc': 'localhost', 'port': '5432', 'dbname': 'aerodrome'}

def GenerateUri(db_config: map):
    return  'postgresql+psycopg2://' + db_config['user'] + ':' + db_config['password'] + '@' + db_config['netloc'] + ':' + db_config['port'] + '/' + db_config['dbname']

db = create_engine(GenerateUri(db_config))
base = declarative_base()


class AirportElement(base):
    __tablename__ = 'icao'

    code = Column(String, primary_key=True)
    name = Column(String)

    def __init__(self, row: list):
        if len(row) == 2:
            self.code = row[0]
            self.name = row[1]


Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)


def CSVToDB(csv_path):
    csvReader = csv.reader(open(csv_path), delimiter=':')
    next(csvReader)
    for row in csvReader:
        element = AirportElement(row)
        session.add(element)


def main():
    session.query(AirportElement).delete()
    session.commit()
    CSVToDB(icao_path)
    session.commit()


if __name__ == '__main__':
    main()
