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

def create_board(data, db_session):
    """
    Assumes that the post is legit to be posted.
    """
    data = apply_transformations(data, db_session)
    new_board = Board(
        name = data['name'],
        address = data['address'],
        description = data.get('description'),
        created_at = data['timestamp'],
        hidden = data.get('hidden'),
        admin_only = data.get('admin_only'),
        read_only = data.get('read_only'),
    )
    db_session.add(new_board)
    db_session.commit()
    return (201, new_board)



def submit_board(data, db_session):
    checkers = [
        {
            "checker": post_checks.is_invalid_data,
        },
        {
            "checker": post_checks.is_board_address_existent,
        },
    ]
    for i in checkers:
        if (i.get('condition') and i['condition'](data, db_session)) or not i.get('condition'):
            err_status = i['checker'](data, db_session)
            if err_status:
                return err_status
    data['timestamp'] = current_timestamp.current_timestamp()
    return create_board(data, db_session)
