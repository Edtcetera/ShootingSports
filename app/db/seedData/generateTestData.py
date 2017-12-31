from app.db.database import Shooter, Member, DropIn, Match, Competitor, Stage, Score, db
import json
import random
import pandas as pd
import numpy as np
import os
from app.db.enums import Status, Pal, Division
import time
from datetime import datetime, timedelta


basedir = os.path.abspath(os.path.dirname(__file__))
SHOOTER_COUNT = 50
MATCH_COUNT = 5
STRINGS_IN_MATCH = 5


def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.
    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%m/%d/%Y', prop)

def generate():
    data = json.load(open(os.path.join(basedir, 'names.json')))
    seedSize = len(data)
    # print("Size of name seed input: " + str(seedSize))

    shooters = pd.DataFrame()
    members = pd.DataFrame()
    dropIns = pd.DataFrame()
    competitors = pd.DataFrame()
    matches = pd.DataFrame()
    stages = pd.DataFrame()
    scores = pd.DataFrame()

    shooters_names = []
    shooters_sid = []

    members_sid = []
    members_mid = []
    members_status = []
    members_pal = []
    members_email = []
    members_ubcID = []
    members_phone = []
    members_startDate = []
    members_endDate = []

    dropIn_sid = []
    dropIn_did = []

    competitor_sid = []
    competitor_division = []
    competitor_isdq = []

    matchid = []
    matches_name = []
    matches_date = []

    stages_stageid = []
    stages_matchid = []

    scores_sid = []
    scores_matchid = []
    scores_stageid = []
    scores_str1 = []
    scores_str2 = []
    scores_str3 = []
    scores_str4 = []
    scores_str5 = []


    for x in range(SHOOTER_COUNT):
        i = random.randint(0, seedSize)
        name = data[i]
        shooters_names.append(name)
        shooters_sid.append(random.randint(0, seedSize))

    nameIndex = 0
    for sid in shooters_sid:
        if random.random() < .7:
            members_sid.append(sid)
            members_mid.append(random.randint(0, seedSize))
            members_status.append(random.choice(list(Status)).name)
            members_pal.append(random.choice(list(Pal)).name)
            members_email.append(shooters_names[nameIndex] + "@gmail.com")
            members_ubcID.append(random.randint(10000000, 99999999))
            members_phone.append(random.randint(1000000000, 9999999999))
            startTimeStr = randomDate("1/1/2014", "1/1/2016", random.random())
            startTimeDate = datetime.strptime(startTimeStr, '%m/%d/%Y')
            members_startDate.append(startTimeDate)
            endTime = startTimeDate + timedelta(days=360)
            endTimeDateStr = (endTime.date().strftime('%m/%d/%Y'))
            endTimeDate = datetime.strptime(endTimeDateStr, '%m/%d/%Y')
            members_endDate.append(endTimeDate)
            nameIndex += 1
        else:
            dropIn_sid.append(sid)
            dropIn_did.append(random.randint(0, seedSize))
            nameIndex += 1
        competitor_sid.append(sid)
        competitor_division.append(random.choice(list(Division)).name)
        competitor_isdq.append(random.choice(['DQ', '']))
        matchid.append(random.randint(1, MATCH_COUNT))
        matches_name.append("Match #" + str(matchid[len(matchid)-1]))

    for id in sorted(list(set(matchid))):
        matchDate = randomDate("1/1/2014", "1/1/2016", random.random())
        matchDateDate = datetime.strptime(matchDate, '%m/%d/%Y')
        matches_date.append(matchDateDate)

    shooters['sid'] = shooters_sid
    shooters['name'] = shooters_names

    members['sid'] = members_sid
    members['mid'] = members_mid
    members['status'] = members_status
    members['pal'] = members_pal
    members['email'] = members_email
    members['ubcID'] = members_ubcID
    members['phone'] = members_phone
    members['startDate'] = members_startDate
    members['endDate'] = members_endDate

    dropIns['sid'] = dropIn_sid
    dropIns['did'] = dropIn_did

    competitors['sid'] = np.random.choice(shooters_sid, SHOOTER_COUNT, replace=False)
    competitors['matchid'] = matchid
    competitors['division'] = competitor_division
    competitors['isdq'] = competitor_isdq

    matches['matchid'] = sorted(list(set(matchid)))
    matches['name'] = sorted(list(set(matches_name)))
    matches['date'] = matches_date

    shooters = shooters.sort_values('sid', 0, True, False, 'quicksort', 'last')
    members = members.sort_values('sid', 0, True, False, 'quicksort', 'last')
    dropIns = dropIns.sort_values('sid', 0, True, False, 'quicksort', 'last')
    competitors = competitors.sort_values('sid', 0, True, False, 'quicksort', 'last')
    matches = matches.sort_values('matchid', 0, True, False, 'quicksort', 'last')

    # for shooterInMatch in competitors['sid']:
    #     print(shooterInMatch)

    #each match gets 5 stages
    for row in matches.itertuples():
        # print(getattr(row, 'matchid'))
        stageCount = 1
        while stageCount <= 5:
            stages_matchid.append(getattr(row, 'matchid'))
            stages_stageid.append(stageCount)
            stageCount += 1

    stages['stageid'] = stages_stageid
    stages['matchid'] = stages_matchid

    #each competitor gets scores in all stages in each match
    for row in competitors.itertuples():
        stageCount = 1
        while stageCount <= 5:
            scores_sid.append(getattr(row, 'sid'))
            scores_matchid.append(getattr(row, 'matchid'))
            scores_stageid.append(stageCount)
            scores_str1.append(random.randint(0, 5000)) #time in ms
            scores_str2.append(random.randint(0, 5000))
            scores_str3.append(random.randint(0, 5000))
            scores_str4.append(random.randint(0, 5000))
            scores_str5.append(random.randint(0, 5000))
            stageCount += 1

    scores['sid'] = scores_sid
    scores['matchid'] = scores_matchid
    scores['stageid'] = scores_stageid
    scores['s1'] = scores_str1
    scores['s2'] = scores_str2
    scores['s3'] = scores_str3
    scores['s4'] = scores_str4
    scores['s5'] = scores_str5

    # print("SHOOTER TABLE")
    # print(shooters)
    # print("MEMBER TABLE")
    # print(members)
    # print("DROPIN TABLE")
    # print(dropIns)
    # print("COMPETITORS TABLE")
    # print(competitors)
    # print("MATCHES TABLE")
    # print(matches)
    # print("STAGES TABLE")
    # print(stages)
    # print("SCORES TABLE")
    # print(scores)

    toSqlTable(shooters, members, dropIns, matches, competitors, stages, scores)


def toSqlTable(shooter, member, dropin, match, competitor, stage, score):
    print("To sql table")
    shooter.to_sql(con=db.engine, name=Shooter.__tablename__, if_exists='replace')
    member.to_sql(con=db.engine, name=Member.__tablename__, if_exists='replace')
    dropin.to_sql(con=db.engine, name=DropIn.__tablename__, if_exists='replace')
    match.to_sql(con=db.engine, name=Match.__tablename__, if_exists='replace')
    competitor.to_sql(con=db.engine, name=Competitor.__tablename__, if_exists='replace')
    stage.to_sql(con=db.engine, name=Stage.__tablename__, if_exists='replace')
    score.to_sql(con=db.engine, name=Score.__tablename__, if_exists='replace')
    print("Finished generating test data")

