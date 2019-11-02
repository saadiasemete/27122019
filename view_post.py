from database import Board, Ban, Post, Captcha
import time
import cfg
from sqlalchemy import and_
from post_checks import *

def view_post(post_data, db_session):
    """
    For now - let us open a single post, then will see.
    """
    fetched_post = db_session.query(Post).filter(id == post_data['post_id'])
    if fetched_post:
        return (200, fetched_post)
    else:
        return (404, "Post with that ID is not found")

def open_post(post_data, db_session):
    checkers = [
        {
            "checker": is_invalid_data,
        },
        {
            "checker": is_board_inexistent,
        },
        #{
        #    "checker": is_thread_inexistent,
        #},
    ]
    for i in checkers:
        if (i.get('condition') and i['condition'](post_data, db_session)) or not i.get('condition'):
            err_status = i['checker'](post_data, db_session)
            if err_status:
                return err_status
    post_data['timestamp'] = int(time.time())
    return view_post(post_data, db_session)