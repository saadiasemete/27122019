from database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
import post_checks
import query_processor

class SubmitPost(query_processor.QueryProcessor):
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

    @classmethod
    def apply_transformations(cls, data, db_session):
        """
        In case the post needs to be changed before getting to the db.
        """
        return data
    
    @classmethod
    def on_checks_passed(cls, data, db_session):
        """
        TODO: permit autofill of board_id if to_thread is specified
        Assumes that the post is legit to be posted.
        """
        data = cls.apply_transformations(data, db_session)
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
            if not data.get('sage'):
                db_session.query(Post).filter(Post.id == data['reply_to']).first().timestamp_last_bump = data['timestamp'] 
        db_session.commit()
        return (201, new_post)