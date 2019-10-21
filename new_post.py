from database import Board, Ban, Post, Captcha
import time
import cfg
from sqlalchemy import and_

def is_invalid_data(post_data, db_session):
    if not isinstance(post_data, dict): #should be a valid json dict
        return "Unparseable post_data"
    try:
        assert board_id #should be not null
        post_data['id_board'] = int(post_data['id_board']) #should be an integer
    except:
        return "Invalid board_id"
    return None

def is_thread(post_data, db_session):
    return not post_data.get('to_thread')

def is_board_inexistent(post_data, db_session):
    board_result = db_session.query(Board.id).filter(Board.id == post_data['id_board']).all()
    if not len(board_result):
        return "board_id does not exist"
    elif len(board_result)>1:
        return "Ambiguous board_id"
    return None

def is_thread_inexistent(post_data, db_session):
    post_result = db_session.query(Post.id).filter(Post.id == post_data['to_thread']).all()
    if not len(post_result):
        return "to_thread does not exist"
    elif len(post_result)>1:
        return "Ambiguous to_thread"
    return None

def is_banned(post_data, db_session):
    ban_result = db_session.query(Ban).filter(Ban.ip_address == post_data['IP'] )
    if db_session.exists(ban_result):
        if post_data['to_thread']:
            if db_session.exists(ban_result.filter(Ban.thread_id == post_data['to_thread'])):
                return "Banned in the thread"
        if db_session.exists(ban_result.filter(Ban.board_id == post_data['id_board'])):
            return "Banned on the board"
    return None

def is_board_rule_violated(post_data, db_session):
    board_result = db_session.query(Board).filter(Board.id == post_data['id_board'] ).first()
    if board_result.read_only:
        return  "This board is read only"
    return None
def is_thread_rule_violated(post_data, db_session):
    """
    Not implemented
    """
    return False

def is_captcha_failed(post_data, db_session):
    if cfg.captcha_on:
        captcha_result = db_session.query(Captcha).filter( 
            and_(
                Captcha.id == post_data['captcha_id'], 
                Captcha.active == True,
                Captcha.timestamp > time.time() - cfg.captcha_lifespan,
            )
        ).first()
        if not captcha_result:
            return "The captcha is invalid or expired"
        elif captcha_result.answer != post_data['captcha_answer']:
            return "Wrong answer to the captcha"

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
                return (False, err_status)

