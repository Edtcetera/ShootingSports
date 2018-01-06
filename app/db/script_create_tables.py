from app.db.database import db


def create():

    db.engine.execute('''CREATE TABLE Shooter (
                          sid BIGINT,
                          name TEXT)''')

    db.engine.execute('''CREATE TABLE Member (
                          mid BIGINT,
                          sid BIGINT,
                          status TEXT,
                          pal TEXT,
                          email TEXT,
                          ubcID BIGINT,
                          phone BIGINT,
                          startDate DATETIME,
                          endDate DATETIME)''')

    db.engine.execute('''CREATE TABLE DropIn (
                          did BIGINT ,
                          sid BIGINT)''')

    db.engine.execute('''CREATE TABLE Match (
                          matchid BIGINT ,
                          name TEXT ,
                          date DATETIME)''')

    db.engine.execute('''CREATE TABLE Competitor (
                            sid INT ,
                            matchid BIGINT,
                            division TEXT,
                            isDQ TEXT)''')

    db.engine.execute('''CREATE TABLE Stage (
                          stageid BIGINT ,
                          matchid BIGINT)''')

    db.engine.execute('''CREATE TABLE Score (
                            sid BIGINT,
                            matchid BIGINT,
                            stageid BIGINT,
                            s1 BIGINT,
                            s2 BIGINT,
                            s3 BIGINT,
                            s4 BIGINT,
                            s5 BIGINT)''')

    print("Tables have been created\n")
