from flask import Flask, request, jsonify
from new_post import submit_post
from view_post import open_post
from new_board import submit_board
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
    return data

def get_data_mimetype_agnostic():
    """
    I'm still figuring this out and not sure
    if I don't need to send anything else
    depending on the mimetype.
    """
    if request.is_json:
        return (append_to_data(request.json),)
    elif request.form:
        return (append_to_data(request.form.to_dict()),)

def json_from_sqlalchemy_row(row):
    row.id #let sqlalchemy refresh the object
    return {i.name: row.__dict__.get(i.name) for i in row.__table__.columns}

@app.route('/api/new_post', methods = ['POST'])
def new_post():
    data = get_data_mimetype_agnostic()
    answer = submit_post(data[0], SA_Session())
    if answer[0]==201: #HTTP 201: CREATED
        response = {
                'result': True,
                'data': json_from_sqlalchemy_row(answer[1]),
            }
    else:
        response = {
                'result': False,
                'data': answer[1],
            }

    return jsonify(response), answer[0]

@app.route('/api/view_post/<int:id>', methods = ['GET'])
def view_post():
    answer = open_post(request.view_args, SA_Session())
    if answer[0]==200: #HTTP 200: OK
        response = {
                'result': True,
                'data': json_from_sqlalchemy_row(answer[1]),
            }
    else:
        response = {
                'result': False,
                'data': answer[1],
            }
    return jsonify(response), answer[0]

@app.route('/api/new_board', methods = ['POST'])
def new_board():
    """
    should be allowed after authorization only
    """
    data = get_data_mimetype_agnostic()
    answer = submit_board(data[0], SA_Session())
    
    if answer[0]==201: #HTTP 201: CREATED
        response = {
                'result': True,
                'data': json_from_sqlalchemy_row(answer[1]),
            }
    else:
        response = {
                'result': False,
                'data': answer[1],
            }
    return jsonify(response), answer[0]

#DELETE AFTER DEBUG
meta.drop_all(engine)
meta.create_all(engine)
app.run(debug = True)