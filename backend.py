from flask import Flask, request
from new_post import submit_post
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)

def json_from_sqlalchemy_row(row):
    return {i.name: row.__dict__.get(i) for i in row.__table__.columns}

@app.route('/api/new_post', methods = ['POST'])
def new_post():
    answer = submit_post(request.form, Session())
    if answer[0]==201: #HTTP 201: CREATED
        response = app.make_response(
            {
                'result': True,
                'data': json_from_sqlalchemy_row(answer[1]),
            }
        )

    else:
        response = app.make_response(
            {
                'result': False,
                'data': answer[1],
            }
        )
    response.status_code = answer[0]
    return response
