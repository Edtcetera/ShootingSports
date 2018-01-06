from app.db.database import db

tables = ['Shooter', 'Member', 'DropIn', 'Match', 'Competitor', 'Stage', 'Score']
auth_tables = ['user', 'roles_users', 'role']


def drop():
    for table in tables:
        try:
            db.engine.execute('''DROP TABLE ''' + table)
        except Exception:
            print('Table ' + table + ' may have already been dropped, continuing to next drop')

def dropAuthUsers():
    for table in auth_tables:
        try:
            db.engine.execute('''DROP TABLE ''' + table)
        except Exception:
            print('Table ' + table + ' may have already been dropped, continuing to next drop')
