import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Crop, Log

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__name__))

# Configure the SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'scms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind the db to the app
db.init_app(app)

# Function to create the physical scms.db file if it doesn't exist yet
def initialize_database():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
