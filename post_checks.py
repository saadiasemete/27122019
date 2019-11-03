from database import Board, Ban, Post, Captcha
import time
import cfg
from sqlalchemy import and_


def is_invalid_data(data, db_session):
    if not isinstance(data, dict): #should be a valid json dict
        return (400, "Unparseable data")
    
    return None

def is_invalid_board_id(data, db_session):
    try:
        assert data['board_id'] #should be not null
        data['board_id'] = int(data['board_id']) #should be an integer
    except:
        return (404, "Invalid board_id")
    return None

def is_thread(data, db_session):
    return not data.get('to_thread')

def is_board_inexistent(data, db_session):
    board_result = db_session.query(Board.id).filter(Board.id == data['board_id']).all()
    if not len(board_result):
        return (404, "board_id does not exist")
    elif len(board_result)>1:
        return (500, "Ambiguous board_id")
    return None


def is_board_address_existent(data, db_session):
    board_address = data.get('board_address', data['address']) #for API clients convenience
    board_result = db_session.query(Board.address).filter(Board.address == board_address).all()
    if len(board_result)==1:
        return (403, "board_address exists")
    elif len(board_result)>1:
        return (500, "Ambiguous board_address")
    return None

def is_thread_inexistent(data, db_session):
    post_result = db_session.query(Post.id).filter(Post.id == data['to_thread']).all()
    if not len(post_result):
        return (404, "to_thread does not exist")
    elif len(post_result)>1:
        return (500, "Ambiguous to_thread")
    return None

def is_banned(data, db_session):
    ban_result = db_session.query(Ban).filter(Ban.ip_address == data['IP'] )
    if db_session.exists(ban_result):
        if data['to_thread']:
            if db_session.exists(ban_result.filter(Ban.thread_id == data['to_thread'])):
                return (403, "Banned in the thread")
        if db_session.exists(ban_result.filter(Ban.board_id == data['board_id'])):
            return (403, "Banned on the board")
    return None

def is_board_rule_violated(data, db_session):
    board_result = db_session.query(Board).filter(Board.id == data['board_id'] ).first()
    if board_result.read_only:
        return  (403, "This board is read only")
    return None
def is_thread_rule_violated(data, db_session):
    """
    Not implemented
    """
    return False

def is_captcha_failed(data, db_session):
    if cfg.captcha_on:
        captcha_result = db_session.query(Captcha).filter( 
            and_(
                Captcha.id == data['captcha_id'], 
                Captcha.active == True,
                Captcha.timestamp > time.time() - cfg.captcha_lifespan,
            )
        ).first()
        if not captcha_result:
            return (403, "The captcha is invalid or expired")
        elif captcha_result.answer != data['captcha_answer']:
            return (403, "Wrong answer to the captcha")