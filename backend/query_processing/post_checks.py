from ..database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_


def is_invalid_data(data, db_session):
    if not isinstance(data, dict): #should be a valid json dict
        return (400, "Unparseable data")
    
    return (None, None)

def is_invalid_board_id(data, db_session):
    try:
        assert data['__data__']['board_id'] #should be not null
        data['__data__']['board_id'] = int(data['__data__']['board_id']) #should be an integer
    except:
        return (404, "Invalid board_id")
    return (None, None)

def is_thread(data, db_session):
    to_thread = data['__data__'].get('to_thread')
    return not is_digit(to_thread) or not int(to_thread)

def is_digit(value):
    return isinstance(value, int) or isinstance(value, str) and value.isdigit()

def is_board_inexistent(data, db_session):
    board_result = db_session.query(Board.id).filter(Board.id == data['__data__']['board_id']).all()
    if not len(board_result):
        return (404, "board_id does not exist")
    elif len(board_result)>1:
        return (500, "Ambiguous board_id")
    return (None, board_result)


def is_board_address_existent(data, db_session):
    try:
        board_address = data['__data__'].get('board_address', data['__data__']['address']) #for API clients convenience
    except:
        return (400, "board_address not included")
    board_result = db_session.query(Board.address).filter(Board.address == board_address).all()
    if len(board_result)==1:
        return (403, "board_address exists")
    elif len(board_result)>1:
        return (500, "Ambiguous board_address")
    return (None, None)

def is_thread_inexistent(data, db_session):
    if not data['__data__'].get('to_thread'):
        return (None, 0)
    
    post_result = db_session.query(Post.id).filter(Post.id == data['__data__']['to_thread']).all()
    if not len(post_result):
        return (404, "to_thread does not exist")
    elif len(post_result)>1:
        return (500, "Ambiguous to_thread")
    return (None, post_result)

def is_banned(data, db_session):
    ban_result = db_session.query(Ban).filter(Ban.ip_address == data['__data__']['ip_address'] )
    if len(ban_result.all()):
        if data['__data__']['to_thread']:
            if len(ban_result.filter(Ban.thread_id == data['__data__']['to_thread']).all()):
                return (403, "Banned in the thread")
        if len(ban_result.filter(Ban.board_id == data['__data__']['board_id']).all()):
            return (403, "Banned on the board")
    return (None, None)

def is_board_rule_violated(data, db_session):
    board_result = db_session.query(Board).filter(Board.id == data['__data__']['board_id'] ).first()
    if board_result.read_only:
        return  (403, "This board is read only") 
    if board_result.thread_requires_attachment and not data['__files__']:
        return  (403, "Attachment required") 
    return (None, board_result)
def is_thread_rule_violated(data, db_session):
    """
    Not implemented
    """
    return (False, None)

def is_captcha_failed(data, db_session):
    #if cfg.captcha_on:
    if data['__config__']['CAPTCHA_ON']:
        captcha_result = db_session.query(Captcha).filter( 
            and_(
                Captcha.id == data['__data__']['captcha_id'], 
                Captcha.active == True,
                Captcha.timestamp > time.time() - data['__config__']['CAPTCHA_LIFESPAN'],
            )
        ).first()
        if not captcha_result:
            return (403, "The captcha is invalid or expired")
        elif captcha_result.answer != data['captcha_answer']:
            return (403, "Wrong answer to the captcha")