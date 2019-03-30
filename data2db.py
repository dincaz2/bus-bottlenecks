import os
import sqlite3
import pandas as pd

def create_db():
    db_name = 'segments_data'
    databaseexisted = os.path.isfile(db_name)
    if databaseexisted:
        os.remove(db_name)
    dbcon = sqlite3.connect(db_name)
    with dbcon:
        #dbcon.execute("PRAGMA foreign_keys = ON")
        cursor = dbcon.cursor()
        cursor.executescript("""
            CREATE TABLE Points (
                Segment           TEXT,
                Geometry          TEXT,
                PRIMARY KEY (Segment, Geometry)
            );

            CREATE TABLE Aliases (
                DicOrder          INTEGER,
                AlphabeticOrder   INTEGER,
                ParentDicOrder    INTEGER,
                Alias             TEXT,
                FOREIGN KEY (DicORder, AlphabeticOrder, ParentDicOrder) REFERENCES Words(DicORder, AlphabeticOrder, ParentDicOrder) ON DELETE CASCADE ON UPDATE CASCADE
            );
            """)
        dbcon.commit()

def segments2db():
    all_segments = pd.read_csv(r'datasets\segments.csv', encoding="utf-8")
    all_segments.to_sql()