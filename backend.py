from flask import Flask, request, jsonify
from flask.views import View
from new_post import SubmitPost
from view_post import OpenPost
from new_board import SubmitBoard
from sqlalchemy import create_engine
from database import meta
import time

from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

#engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:///here.db', echo=True)
SA_Session = sessionmaker(bind=engine)

def append_to_data(data):
    app.config.from_json("cfg.json")
    data['__headers__'] = request.headers
    data['__config__'] = app.config
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


class StandardRequest(View):
    data_fetcher = get_data_mimetype_agnostic
    target_status = 200
    query_processor = NotImplemented
    answer_processor = json_from_sqlalchemy_row
    def dispatch_request(self):
        data = self.__class__.data_fetcher()
        db_session = SA_Session()
        answer = self.__class__.query_processor.process(data[0], db_session)
        db_session.close()
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

app.add_url_rule('/api/new_board', view_func = NewBoard.as_view('new_board'), methods = ['POST'])
app.add_url_rule('/api/new_post', view_func = NewPost.as_view('new_post'), methods = ['POST'])

#DELETE AFTER DEBUG
meta.drop_all(engine)
meta.create_all(engine)
app.run(debug = True)