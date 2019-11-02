from database import Board, Ban, Post, Captcha
import time
import cfg
from sqlalchemy import and_
from post_checks import *


def apply_transformations(post_data, db_session):
    """
    In case the post needs to be changed before getting to the db.
    """
    return post_data

def create_post(post_data, db_session):
    """
    Assumes that the post is legit to be posted.
    """
    post_data = apply_transformations(post_data, db_session)
    new_post = Post(
        id_board = post_data['board_id'],
        id_thread = post_data.get('to_thread'),
        reply_to = post_data.get('reply_to'),
        ip_address = post_data['ip_address'],
        title = post_data.get('title'),
        text  = post_data.get('text'),
        tripcode = post_data.get('tripcode'),
        #password = post_data.get('password'),
        sage = bool(post_data.get('sage')),
        timestamp = post_data['timestamp'],
    )
    db_session.add(new_post)
    if is_thread(post_data, db_session):
        new_post.timestamp_last_bump = post_data['timestamp']
    else:
        db_session.query(Post).filter(id == post_data['reply_to']).first().timestamp_last_bump = post_data['timestamp'] 
    db_session.commit
    return (201, new_post)



def submit_post(post_data, db_session):
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
        if (i.get('condition') and i['condition'](post_data, db_session)) or not i.get('condition'):
            err_status = i['checker'](post_data, db_session)
            if err_status:
                return err_status
    post_data['timestamp'] = int(time.time())
    return create_post(post_data, db_session)
