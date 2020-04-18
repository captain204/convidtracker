from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db
from views import tracker_blueprint

def create_app(config_filename):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_filename)
    db.init_app(app)
    app.register_blueprint(tracker_blueprint, url_prefix='/tracker')
    migrate = Migrate(app, db)
    return app


app = create_app('config')


