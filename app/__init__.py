from flask import Flask
from app.util.util import gzipped
from bcrypt import gensalt


# Define the WSGI application object
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = gensalt()
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 2628000           # This caches all static files (1 month)
app.config.from_object('config')


# Import a module / component using its blueprint handler variable (labels) -> Import all the controllers
from app.db.database import db_setup as database_route
from app.queries.main import queries as queries_route
from app.util.compress import compress as static_compress


# Register blueprint(s)
app.register_blueprint(database_route)
app.register_blueprint(queries_route)
app.register_blueprint(static_compress)
