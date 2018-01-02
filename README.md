# AMS Shooting Sports at UBC
## Club website - membership tracking and scoring
### by Edward Cai - forked off of CPSC304 project

### Requirements
- Python 3.5 and later
- Windows: Microsoft Visual C++ Build Tools
- pip install -r requirements.txt

### Steps to run
- Go to config.py and uncomment the database and environment you are working with
- Run script_reset_db.py to DROP(script_drop_data.py), CREATE(script_create_tables.py), and INSERT(generateTestData.py) randomized competitor/match/score data
- Randomized player names and email are seeded from names.json
- Run app.py to host the app locally on port 5000
- :stars: Run example queries from below :stars:

### Example queries
#### View expiring memberships within X months
- Available arguments: integer
- http://127.0.0.1:5000/member_expiry?time_frame=100

#### View individual tables
- Available arguments: shooter, member, dropIn, match, competitor, stage, score table
- http://127.0.0.1:5000/db_tables?table_name=shooter

#### View rankings for a particular match by division or overall. Excluding Disqualified (DQ'd) competitors.
- Available arguments: open, standard, classic, production, revolver, production_optics, overall
- http://127.0.0.1:5000/match_ranking?match_id=1&division=overall
