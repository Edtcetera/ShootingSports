#!flask/bin/python
from app import app
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from sqlalchemy.exc import OperationalError
from app.db.database import User, Role, db

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    try:
        if user_datastore.get_user('test@test.com') is None:
            print('Test user not present, creating test user')
            user_datastore.create_user(email='test@test.com', password=hash_password('password'))
    except OperationalError:
        print('User table is not initiated, creating test user and inserting')
        user_datastore.create_user(email='test@test.com', password=hash_password('password'))
    db.session.commit()

app.run()
