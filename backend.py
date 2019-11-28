from flask import Flask, request, jsonify, current_app
from flask.views import View
from new_post import SubmitPost
from view_post import OpenPost
from new_board import SubmitBoard
from sqlalchemy import create_engine
from database import meta
import time

from sqlalchemy.orm import sessionmaker, scoped_session

def read_db_engine(config):
    """
    Might make it more user-friendly later
    """
    return config['DB_ENGINE']

def generate_app(config_file = "cfg.json"):
    app = Flask("pyexaba")
    app.session_generator = sessionmaker()
    app.config_file = config_file
    app.config.from_json(current_app.config_file)
    engine = create_engine(read_db_engine(app.config), echo=True)
    if app.config['DEBUG']:
        pass
    else:
        pass
    if app.config['TESTING']:
        meta.drop_all(engine)
        meta.create_all(engine)
    else:
        pass
    
    return app

#engine = create_engine('sqlite:///:memory:', echo=True)

#db_session = scoped_session(sessionmaker(bind=engine))

def append_to_data(data):
    current_app.config.from_json(current_app.config_file) #include in a factory
    data['__headers__'] = request.headers
    data['__config__'] = current_app.config
    data['__files__'] = request.files
    data['ip_address'] = request.remote_addr
    return data

def get_data_mimetype_agnostic():
    """
    I'm still figuring this out and not sure
    if I don't need to send anything else
    depending on the mimetype.
    """
    if request.is_json:
        result = request.json
    elif request.form:
       result = request.form.to_dict()
    elif request.method == 'GET':
        result = request.view_args if request.view_args else {}
    return (append_to_data(result),)


def json_from_sqlalchemy_row(row):
    row.id #let sqlalchemy refresh the object
    return {i.name: row.__dict__.get(i.name) for i in row.__table__.columns}

@current_app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

class StandardRequest(View):
    data_fetcher = get_data_mimetype_agnostic
    target_status = 200
    query_processor = NotImplemented
    answer_processor = json_from_sqlalchemy_row
    def dispatch_request(self):
        data = self.__class__.data_fetcher()
        db_session = current_app.session_generator(
            bind = create_engine(read_db_engine(current_app.config), echo=True)
        )
        answer = self.__class__.query_processor.process(data[0], db_session)
        if answer[0]==201: #HTTP 201: CREATED
            response = {
                    'result': True,
                    'data': self.__class__.answer_processor(answer[1]),
                }
        else:
            response = {
                    'result': False,
                    'data': answer[1],
                }
        return jsonify(response), answer[0]

class NewBoard(StandardRequest):
    target_status = 201
    query_processor = SubmitBoard

class NewPost(StandardRequest):
    target_status = 201
    query_processor = SubmitPost

class ViewPost(StandardRequest):
    target_status = 200
    query_processor = OpenPost

current_app.add_url_rule('/api/new_board', view_func = NewBoard.as_view('new_board'), methods = ['POST'])
current_app.add_url_rule('/api/new_post', view_func = NewPost.as_view('new_post'), methods = ['POST'])

#DELETE AFTER DEBUG

#generate_app()