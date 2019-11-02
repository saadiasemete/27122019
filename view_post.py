from database import Board, Ban, Post, Captcha
import time
import cfg
from sqlalchemy import and_
from post_checks import is_invalid_data, is_board_inexistent

def view_post(data, db_session):
    """
    For now - let us open a single post, then will see.
    """
    fetched_post = db_session.query(Post).filter(id == data['post_id'])
    if fetched_post:
        return (200, fetched_post)
    else:
        return (404, "Post with that ID is not found")

def open_post(data, db_session):
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
        if (i.get('condition') and i['condition'](data, db_session)) or not i.get('condition'):
            err_status = i['checker'](data, db_session)
            if err_status:
                return err_status
    data['timestamp'] = int(time.time())
    return view_post(data, db_session)