from flask import Flask, request, jsonify, current_app, send_from_directory
from flask.views import View
from flask import Blueprint
from .query_processing import SubmitBoard, SubmitPost, OpenPost
from .query_processing import utils as query_utils
from sqlalchemy import create_engine
from sqlalchemy.sql import sqltypes
from sqlalchemy.orm import collections
import time
import datetime
from sqlalchemy.inspection import inspect

from sqlalchemy.orm import sessionmaker, scoped_session

app_blueprint = Blueprint(
    "pyexaba_backend",
    "backend_blueprint", #wtf is an import name?
)

def read_db_engine(config):
    """
    Might make it more user-friendly later
    """
    return config['DB_ENGINE']



#engine = create_engine('sqlite:///:memory:', echo=True)

#db_session = scoped_session(sessionmaker(bind=engine))

def simplify_imd(imd):
    """
    Werkzeug's IMD is a huge pain.
    """
    target_dict = imd.to_dict(flat = False)
    return {i:(j[0] if len(j) == 1 else j) for i,j in target_dict.items()}

def expand_filelist(files):
    return {str(i): j for i,j in enumerate(files.getlist('files'))}


def append_to_data(data):
    current_app.config.from_json(current_app.config_file) #include in a factory
    data['__headers__'] = request.headers
    data['__config__'] = current_app.config
    data['__files__'] = expand_filelist(request.files)
    print(data['__files__'])
    data['__data__']['ip_address'] = request.remote_addr
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
       result = simplify_imd(request.form)
    elif request.method == 'GET':
        result = simplify_imd(request.args) if request.args else {}
    wrapper = {'__data__': result}
    return (append_to_data(wrapper),)

def preprocess_sqlalchemy_values(column, value):
    if isinstance(value, datetime.datetime) and value:
        return value.isoformat()
    elif isinstance(value, collections.InstrumentedList): #meaning it represents one-to-many backref
        if column == "attachments":
            return process_attachments(value)
    return value


def json_from_sqlalchemy_row(row):
    row.id #let sqlalchemy refresh the object
    result = {}
    for i,j in dict(inspect(row).attrs).items():
        result[i] = preprocess_sqlalchemy_values(i, j.value)
    return result

def process_attachments(attachments):

    return [
        query_utils.generate_path_to_attachment(
        i.mediatype,
        i.filename,
        i.extension,
        current_app.config['PATH']['__PREFIX__'],
        current_app.config['PATH'][i.mediatype.upper()],
        False
    )
    for i in attachments
    ]
        

def unfold_post_list(post_list):
    result_prima = {}
    """
    result = {
        "post_id": {
            "post": post_obj
            "tripcode": trip_obj
            "attachments": [att1, att2, ...]
        }
    }
    """
    for i in post_list:
        result_prima.setdefault(
            i.Post.id, {"post": i.Post, 
            #"tripcode": i.Tripcode, 
            "attachments": [],}
            )['attachments'].append(i.Attachment)
    result_secunda = []
    for i, j in result_prima.items():
        result_secunda.append(
            {
                "post": json_from_sqlalchemy_row(j['post']),
                #json_from_sqlalchemy_row(j['Tripcode']),
                "attachments": process_attachments(j['attachments']),
            }
        )
    return result_secunda

def unf_list(input_list):

    return  [
        json_from_sqlalchemy_row(i)
        for i in input_list
    ]


class StandardRequest(View):
    
    data_fetcher = get_data_mimetype_agnostic
    target_status = 200
    query_processor = NotImplemented
    answer_processor = json_from_sqlalchemy_row
    def dispatch_request(self):
        
        data = self.__class__.data_fetcher()
        db_session = current_app.session_generator(
            bind = current_app.sql_engine
        )
        answer = self.__class__.query_processor.process(data[0], db_session)
        if answer[0]==self.target_status:
            response = {
                    'result': True,
                    'data': self.__class__.answer_processor(answer[1]),
                    'info': None,
                }
        else:
            response = {
                    'result': False,
                    'data': answer[1],
                    'info': None if len(answer)==2 else answer[2], #for details on errors
                }
        db_session.close()
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
    answer_processor = unf_list

app_blueprint.add_url_rule('/api/new_board', view_func = NewBoard.as_view('new_board'), methods = ['POST'])
app_blueprint.add_url_rule('/api/new_post', view_func = NewPost.as_view('new_post'), methods = ['POST'])
app_blueprint.add_url_rule('/api/view_post', view_func = ViewPost.as_view('view_post'), methods = ['GET'])

#DELETE AFTER DEBUG

#generate_app()