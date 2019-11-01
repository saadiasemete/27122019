from database import Board, Ban, Post, Captcha
import time
import cfg
from sqlalchemy import and_

def is_invalid_data(post_data, db_session):
    if not isinstance(post_data, dict): #should be a valid json dict
        return (400, "Unparseable post_data")
    try:
        assert board_id #should be not null
        post_data['id_board'] = int(post_data['id_board']) #should be an integer
    except:
        return (404, "Invalid board_id")
    return None

def is_thread(post_data, db_session):
    return not post_data.get('to_thread')

def is_board_inexistent(post_data, db_session):
    board_result = db_session.query(Board.id).filter(Board.id == post_data['id_board']).all()
    if not len(board_result):
        return (404, "board_id does not exist")
    elif len(board_result)>1:
        return (500, "Ambiguous board_id")
    return None

def is_thread_inexistent(post_data, db_session):
    post_result = db_session.query(Post.id).filter(Post.id == post_data['to_thread']).all()
    if not len(post_result):
        return (404, "to_thread does not exist")
    elif len(post_result)>1:
        return (500, "Ambiguous to_thread")
    return None

def is_banned(post_data, db_session):
    ban_result = db_session.query(Ban).filter(Ban.ip_address == post_data['IP'] )
    if db_session.exists(ban_result):
        if post_data['to_thread']:
            if db_session.exists(ban_result.filter(Ban.thread_id == post_data['to_thread'])):
                return (403, "Banned in the thread")
        if db_session.exists(ban_result.filter(Ban.board_id == post_data['id_board'])):
            return (403, "Banned on the board")
    return None

def is_board_rule_violated(post_data, db_session):
    board_result = db_session.query(Board).filter(Board.id == post_data['id_board'] ).first()
    if board_result.read_only:
        return  (403, "This board is read only")
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
            return (403, "The captcha is invalid or expired")
        elif captcha_result.answer != post_data['captcha_answer']:
            return (403, "Wrong answer to the captcha")

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
    current_time = int(time.time())
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
