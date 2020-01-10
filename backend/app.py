from .blueprint import read_db_engine, app_blueprint
from flask import Flask
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .database import meta

def generate_app(config_file = "cfg.json"):
    app = Flask("pyexaba")
    app.register_blueprint(app_blueprint)
    print(app_blueprint)
    with app.app_context():
        app.session_generator = sessionmaker()
        app.config_file = config_file
        app.config.from_json(app.config_file)
        app.sql_engine = create_engine(read_db_engine(app.config), echo=False)
        if app.config['DEBUG']:
            pass
        else:
            pass
        if app.config['TESTING']:
            meta.drop_all(app.sql_engine)
            meta.create_all(app.sql_engine)
        else:
            pass
    print(app.url_map)
    return app