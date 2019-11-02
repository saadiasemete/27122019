from database import Board, Ban, Post, Captcha
import time
import cfg
from sqlalchemy import and_
from post_checks import *


def apply_transformations(data, db_session):
    """
    In case the post needs to be changed before getting to the db.
    """
    return data

def create_post(data, db_session):
    """
    Assumes that the post is legit to be posted.
    """
    data = apply_transformations(data, db_session)
    new_post = Post(
        id_board = data['board_id'],
        id_thread = data.get('to_thread'),
        reply_to = data.get('reply_to'),
        ip_address = data['ip_address'],
        title = data.get('title'),
        text  = data.get('text'),
        tripcode = data.get('tripcode'),
        #password = data.get('password'),
        sage = bool(data.get('sage')),
        timestamp = data['timestamp'],
    )
    db_session.add(new_post)
    if is_thread(data, db_session):
        new_post.timestamp_last_bump = data['timestamp']
    else:
        db_session.query(Post).filter(id == data['reply_to']).first().timestamp_last_bump = data['timestamp'] 
    db_session.commit
    return (201, new_post)



def submit_post(data, db_session):
    """
    The order of checks matters for user experience.
    It should be this way:
    1. Schema check: preventing malformed requests.
    2. Ban check (all levels): goes BEFORE everything else. People shouldn't waste time.
    3. Requirements check (all levels).
    4. Captcha check: only when everything else is fine.
    """
    checkers = [
        {
            "checker": is_invalid_data,
        },
        {
            "checker": is_board_inexistent,
        },
        {
            "checker": is_thread_inexistent,
            "condition": is_thread,
        },
        {
            "checker": is_banned,
        },
        {
            "checker": is_thread_rule_violated,
            "condition": is_thread,
        },
        {
            "checker": is_board_rule_violated,
        },
        {
            "checker": is_captcha_failed,
            "condition": lambda a,b: False,
        },
    ]
    for i in checkers:
        if (i.get('condition') and i['condition'](data, db_session)) or not i.get('condition'):
            err_status = i['checker'](data, db_session)
            if err_status:
                return err_status
    data['timestamp'] = int(time.time())
    return create_post(data, db_session)
