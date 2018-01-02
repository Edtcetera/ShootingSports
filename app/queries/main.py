from app.util.util import gzipped
from app.db.database import Shooter, Member, DropIn, Match, Competitor, Stage, Score, db
from app.db.enums import Status, Pal, Division
from flask import Blueprint, request, render_template, jsonify
import datetime
from sqlalchemy import and_, text
from sqlalchemy.orm.session import sessionmaker
from dateutil.relativedelta import relativedelta


# Define the blueprint: 'queries'
queries = Blueprint('queries', __name__)
# global scope
Session = sessionmaker(bind=db.engine)


@queries.route('/')
@gzipped
def load():
    """
    Loads the HTML template
    """
    return render_template("dashboard.html")

@queries.route('/db_tables', methods=['GET'])
def get_tables():
    """
    Gets all rows for all tables
    :return:
    """
    tables_map = {
        "shooter": Shooter.__table__.columns.keys(),
        "member": Member.__table__.columns.keys(),
        "dropIn": DropIn.__table__.columns.keys(),
        "match": Match.__table__.columns.keys(),
        "competitor": Competitor.__table__.columns.keys(),
        "stage": Stage.__table__.columns.keys(),
        "score": Score.__table__.columns.keys()
    }

    table_name = request.args.get('table_name').lower()
    available_tables = ['shooter', 'member', 'dropIn', 'match',
                        'competitor', 'stage', 'score']

    if table_name in available_tables:
        sql = text("""SELECT * FROM """ + table_name)
        rows = db.engine.execute(sql)

        headers = tables_map[table_name]
        data = [list(row[1:]) for row in rows]
        return jsonify({
            'code': 200,
            'table': table_name,
            'entries': data,
            'headers': headers
        })

    else:
        return jsonify({
            'code': 400,
            'error': 'Table Name was not valid'
    })

@queries.route('/match_ranking', methods =['GET'])
def get_match_ranking():
    """
    Given a match id, shows the rankings of participating competitors
    The lower the overall match time, the higher ranking the player
    Stage rank is determined by average of lowest 4 times
    Match rank is determined by aggregating all average stage times
    Excludes DQ'd competitors
    """

    match_id = request.args.get('match_id')
    try:
        match_id = int(match_id)
        print(match_id)
    except ValueError as e:
        print(e)
        return jsonify({
            'code': 400,
            'error': 'Not valid match id, must be an int'
        })
    session = Session()

    existing_matches = []
    existing_matches_query = session.query(Match)

    for match in existing_matches_query:
        existing_matches.append(match.matchid)

    if match_id not in existing_matches:
        return jsonify({
            'code': 400,
            'error': 'No such match exists in database'
        })

    scores_in_match = session.query(Score, Competitor, Shooter) \
        .filter(Score.matchid == match_id)\
        .join(Competitor, and_(Competitor.sid == Score.sid, Competitor.matchid == Score.matchid))\
        .filter(Competitor.isDQ != 'DQ')\
        .join(Shooter, Score.sid == Shooter.sid)

    stage_scores = []
    last_competitor = -1
    for stage_score in scores_in_match:
        if (last_competitor != stage_score.Shooter.sid):
            last_competitor = stage_score.Shooter.sid
        stage_strings = []
        average_stage_time = 0
        stage_strings.append(float(stage_score.Score.s1))
        stage_strings.append(float(stage_score.Score.s2))
        stage_strings.append(float(stage_score.Score.s3))
        stage_strings.append(float(stage_score.Score.s4))
        stage_strings.append(float(stage_score.Score.s5))
        stage_strings.sort()
        stage_strings.pop() #Drop the highest time

        for string in stage_strings:
            average_stage_time += string
        average_stage_time = average_stage_time / 4 #average for 4 strings (exclude dropped)

        stage_score = {
            "name": stage_score.Shooter.name,
            "sid": stage_score.Shooter.sid,
            "stage_number": stage_score.Score.stageid,
            "average_stage_time": average_stage_time
        }
        stage_scores.append(stage_score)

    last_competitor = -1
    competitor_scores = []
    for stage_score in stage_scores:
        if (last_competitor != stage_score["sid"]):
            last_competitor = stage_score["sid"]
            competitor = {
                "name": stage_score["name"],
                "sid": stage_score["sid"],
                "time": stage_score["average_stage_time"]
            }
            competitor_scores.append(competitor)
        else:
            competitor_scores[len(competitor_scores)-1]["time"] += stage_score["average_stage_time"]

    ranked_competitors = sorted(competitor_scores, key=lambda k: k['time'])

    return jsonify({
        'code': 200,
        'table': 'Match ' + str(match_id) + " ranking",
        'entries': ranked_competitors
    })


@queries.route('/member_expiry', methods =['GET'])
def get_expiry():
    """
    Returns the membership IDs of memberships expiring within 'time_frame' amount of MONTHS
    """

    time_frame = request.args.get('time_frame')
    try:
        time_frame = int(time_frame)
    except ValueError as e:
        print(e)
        return jsonify({
            'code': 400,
            'error': 'Not valid monthly time frame, should only be int'
        })

    expiring_members = []
    session = Session()
    now = datetime.date.today()
    relativeMonths = now - relativedelta(months=time_frame)
    memberShooterTable = session.query(Member, Shooter) \
        .join(Shooter) \
        .filter(and_(Member.endDate > relativeMonths, Member.status != Status.EXPIRED))
    print("Memberships expiring with " + str(time_frame) + " months")
    for row in memberShooterTable:
        print(row)
        print(row.Member.email)
        print(row.Shooter.name)
        returnMember = {'name': row.Shooter.name,
                        'mid': row.Member.mid,
                        'email': row.Member.email,
                        'endDate': row.Member.endDate}
        expiring_members.append(returnMember)

    return jsonify({
        'code': 200,
        'table': 'Expiring Members',
        'entries': expiring_members
    })

# """ SELECT QUERIES """
#
#
# @queries.route('/db_tables', methods=['GET'])
# def get_tables():
#     """
#     Gets all the rows for a table in the DB
#     :return: JSON string containing all the rows in a particular table
#     """
#     tables_map = {
#         "athlete": Athlete.__table__.columns.keys(),
#         "coach": Coach.__table__.columns.keys(),
#         "competition": Competition.__table__.columns.keys(),
#         "game": Game.__table__.columns.keys(),
#         "gamegoal": GameGoal.__table__.columns.keys(),
#         "season": Season.__table__.columns.keys(),
#         "stadium": Stadium.__table__.columns.keys(),
#         "team": Team.__table__.columns.keys()
#     }
#
#     table_name = request.args.get('table_name').lower()
#     available_tables = ['athlete', 'coach', 'competition', 'game', 'gamegoal', 'season', 'stadium', 'team']
#
#     if table_name in available_tables:
#         sql = text('''SELECT * FROM ''' + table_name)
#         rows = db.engine.execute(sql)
#
#         headers = tables_map[table_name]
#         data = []
#         if table_name == "game":
#             for r in rows:
#                 data.append([r[6], r[9], r[3], r[4], r[5], r[7]])
#         elif table_name == "competition":
#             for r in rows:
#                 data.append([r[1], r[2], r[3]])
#         else:
#             data = [list(row[1:]) for row in rows]
#
#         return jsonify({'code': 200, 'table': table_name, 'entries': data, 'headers': headers})
#
#     return jsonify({'code': 400, 'error': 'Table Name was not valid'})
#
#
# """ INSERT QUERIES """
#
#
# @queries.route('/insert_query', methods=['GET', 'POST'])
# @gzipped
# def insert_query():
#     """Insert data for Athlete, Team or Coach"""
#     insert_table = request.form['table_name']
#
#     # Athlete fields
#     a_name = request.form['a_name']
#     a_status = request.form['a_status']
#     # Team fields
#     t_name = request.form['t_name']
#     t_loc = request.form['t_location']
#
#     if insert_table == "Athlete":
#         last_id = int(db.session.query(Athlete).order_by(Athlete.id.desc()).first().id)
#         table = 'Athlete (id, Salary, Name, DOB, Status, placeOfBirth, countryID, goals, assists, wins, losses)'
#         vals = 'VALUES (' + str(last_id + 1) + ', 999999, "' + a_name + '", "1970-01-05", "' + a_status + '", "Canada", "Canada", 15, 10, 10, 0)'
#     elif insert_table == "Team":
#         team_exists = db.session.query(Team).filter_by(teamID=t_name).count()
#         table = 'Team (teamID, location, dateCreated, goals, assists, wins, losses)'
#         vals = 'VALUES ("' + t_name + '", "' + t_loc + '", "2018-01-01", 168, 153, 55, 20)'
#     else:
#         return jsonify({'error': "Invalid Table Name"})
#
#     sql = text('''INSERT INTO ''' + table + vals)
#
#     if insert_table == "Team" and team_exists > 0:
#         pass
#     else:
#         db.engine.execute(sql)                                      # Runs the SQL INSERT
#
#     if insert_table == "Athlete":
#         row = db.session.query(Athlete).order_by(Athlete.id.desc()).limit(5).all()
#         last_vals = [[r.id, r.salary, r.name, r.dob, r.status, r.placeOfBirth, r.countryID, r.goals, r.assists, r.wins, r.losses]
#                      for r in row]
#     elif insert_table == "Team":
#         row = db.session.query(Team).order_by(Team.teamID.desc()).all()
#         last_vals = [[r.teamID, r.location, r.dateCreated, r.goals, r.assists, r.wins, r.losses] for r in row]
#
#
#     return jsonify({
#         'code': 200,
#         'query_type': 'INSERT',
#         'table': insert_table,
#         'entries': last_vals
#     })
#
#
# """ DELETE QUERIES """
#
#
# @queries.route('/delete_query', methods=['GET', 'POST'])
# @gzipped
# def delete_query():
#     """Delete from Stadium or Team"""
#
#     delete_table = request.form['table_name']
#
#     # Stadium fields
#     s_name = request.form['s_name'].replace("-", " ") + " "
#     s_location = request.form['s_location']
#     # Team fields
#     t_name = request.form['t_name']
#
#     if delete_table == "Stadium":
#         sql = text('''DELETE FROM Stadium WHERE name ="''' + s_name + '''" AND location ="''' + s_location + '"')
#     elif delete_table == "Team":
#         sql = text('''DELETE FROM Team WHERE teamID ="''' + t_name + '"')
#     else:
#         return jsonify({'error': "Invalid Table Name"})
#
#     db.engine.execute(sql)
#
#     if delete_table == "Stadium":
#         row = db.session.query(Stadium).order_by(Stadium.name.asc()).all()
#         last_vals = [[r.name, r.location] for r in row]
#     elif delete_table == "Team":
#         row = db.session.query(Team).order_by(Team.teamID.asc()).all()
#         last_vals = [[r.teamID, r.location, r.dateCreated, r.goals, r.assists, r.wins, r.losses] for r in row]
#
#     return jsonify({
#         'code': 200,
#         'query_type': 'DELETE',
#         'table': delete_table,
#         'entries': last_vals
#     })
#
#
# """ UPDATE QUERIES """
#
#
# @queries.route('/update_player_stats', methods=['GET', 'POST'])
# @gzipped
# def update_query_salary():
#     """Updates the salary of a certain player"""
#
#     p_keys = {
#         "Messi": 238,
#         "Ronaldo": 190,
#         "Neymar": 200
#     }
#
#     player_salary = request.args.get('new_salary')
#     player_key = request.args.get('player_name')
#
#     sql = text('''UPDATE Athlete SET salary = ''' + player_salary + ''' WHERE id = ''' + str(p_keys[player_key]))
#     db.engine.execute(sql)
#
#     # Select player with updated salary
#     sql = text('''SELECT Athlete.name, Athlete.salary FROM Athlete WHERE id = ''' + str(p_keys[player_key]))
#     data = db.engine.execute(sql)
#     json_data = [list(row) for row in data]
#
#     return jsonify({
#         'code': 200,
#         'query_type': 'UPDATE',
#         'table': "Athlete",
#         'entries': json_data
#     })
#
#
# @queries.route('/update_player_country', methods=['GET', 'POST'])
# @gzipped
# def update_query_country():
#     """Updates the country of a certain player"""
#
#     p_keys = {
#         "Messi": 238,
#         "Ronaldo": 190,
#         "Neymar": 200
#     }
#
#     player_country = request.args.get('new_country')
#     player_key = request.args.get('player_name')
#
#     sql = text('''UPDATE Athlete SET countryID = "''' + player_country + '''" WHERE id = ''' + str(p_keys[player_key]))
#     db.engine.execute(sql)
#
#     # Select player with updated salary
#     sql = text('''SELECT Athlete.name, Athlete.countryID FROM Athlete WHERE id = ''' + str(p_keys[player_key]))
#     data = db.engine.execute(sql)
#     json_data = [list(row) for row in data]
#
#     return jsonify({
#         'code': 200,
#         'query_type': 'UPDATE',
#         'table': "Athlete",
#         'entries': json_data
#     })
#
# """ JOIN QUERIES """
#
#
# @queries.route('/join_query', methods=['GET'])
# @gzipped
# def join_query():
#     sql = ''
#     qry_num = int(request.args.get('qry'))
#
#     if qry_num == 1:
#         sql = helper.join_2_query1()
#     elif qry_num == 2:
#         sql = helper.join_2_query2()
#     elif qry_num == 3:
#         sql = helper.join_3_query()
#
#     data = db.engine.execute(sql)
#     json_data = [list(row) for row in data]
#
#     return jsonify({
#         'code': 200,
#         'query_type': 'JOIN',
#         'entries': json_data
#     })
#
#
# """ GROUP BY QUERIES """
#
#
# @queries.route('/groupby_query', methods=['GET'])
# @gzipped
# def groupby_query():
#     """Find the number of players in each club team who are not born in the country the club is located in"""
#
#     sql = text('''SELECT t.teamID, count(*) FROM Athlete a, Team t
#                   WHERE a.teamID = t.teamID AND t.location <> a.countryID
#                   GROUP BY t.teamID''')
#
#     data = db.engine.execute(sql)
#     a_data = [list(row) for row in data]
#     json_data = helper.select_groupby_table(data=a_data)
#
#     return jsonify({
#         'code': 200,
#         'query_type': 'GROUP BY',
#         'table': 'Team',
#         'entries': json_data
#     })
#
#
# """ CREATE VIEW QUERY """
#
#
# @queries.route('/create_view_query', methods=['GET'])
# @gzipped
# def create_view():
#     """Manager Performance view -
#         - Only care about Name, position and current stats
#     """
#
#     tb_exists = "SELECT count(*) FROM sqlite_master WHERE type='view' AND name='AthletePerformanceView'"
#     row = db.engine.execute(tb_exists)
#     if str(row.fetchone()) == '(1,)':
#         print("Create View already created")
#
#     else:
#         sql = text('''CREATE VIEW AthletePerformanceView AS
#                     SELECT Athlete.Name, Athlete.Position, Athlete.Goals, Athlete.Assists, Athlete.Wins, Athlete.Losses
#                     FROM Athlete''')
#         db.engine.execute(sql)
#
#     qry_view = text('''SELECT * FROM AthletePerformanceView''')         # View Table
#     rows = db.engine.execute(qry_view)
#     json_data = [list(row) for row in rows]
#
#     return jsonify({
#         'code': 200,
#         'query_type': 'CREATE VIEW',
#         'entries': json_data
#     })
