from database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
import post_checks
import current_timestamp


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
        board_id = data['board_id'],
        to_thread = data.get('to_thread'),
        reply_to = data.get('reply_to'),
        ip_address = data['ip_address'],
        title = data.get('title'),
        text  = data.get('text'),
        #tripcode = data.get('tripcode'),
        #password = data.get('password'),
        sage = bool(data.get('sage')),
        timestamp = data['timestamp'],
    )
    db_session.add(new_post)
    if post_checks.is_thread(data, db_session):
        new_post.timestamp_last_bump = data['timestamp']
    else:
        db_session.query(Post).filter(Post.id == data['reply_to']).first().timestamp_last_bump = data['timestamp'] 
    db_session.commit()
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
            "checker": post_checks.is_invalid_data,
        },
        {
            "checker": post_checks.is_invalid_board_id,
        },
        {
            "checker": post_checks.is_board_inexistent,
        },
        {
            "checker": post_checks.is_thread_inexistent,
            "condition": post_checks.is_thread,
        },
        {
            "checker": post_checks.is_banned,
        },
        {
            "checker": post_checks.is_thread_rule_violated,
            "condition": post_checks.is_thread,
        },
        {
            "checker": post_checks.is_board_rule_violated,
        },
        {
            "checker": post_checks.is_captcha_failed,
            "condition": lambda a,b: False,
        },
    ]
    for i in checkers:
        if (i.get('condition') and i['condition'](data, db_session)) or not i.get('condition'):
            err_status = i['checker'](data, db_session)
            if err_status:
                return err_status
    data['timestamp'] = current_timestamp.current_timestamp()
    return create_post(data, db_session)
