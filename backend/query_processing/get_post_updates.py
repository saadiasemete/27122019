from ..database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
from . import post_checks, query_processor, utils

class PostUpdates(query_processor.QueryProcessor):
    checkers = [
        {
            "checker": post_checks.is_invalid_data,
        },
        {
            "checker": post_checks.is_correct_update_query,
        },
        {
            "checker": post_checks.is_timestamp_present,
        },
        {
            "checker": post_checks.is_thread_inexistent,
            "condition": lambda data, db_session: data['__checkers__']['is_correct_update_query']['type']=='thread',
            "args": ['thread_id']
        },
        {
            "checker": post_checks.is_board_inexistent,
            "condition": lambda data, db_session: data['__checkers__']['is_correct_update_query']['type']=='board',
        },
        {
            "checker": post_checks.is_post_inexistent,
            "condition": lambda data, db_session: data['__checkers__']['is_correct_update_query']['type']=='post',
            "args": ['post_id']
        },
    ]

    @classmethod
    def on_checks_passed(cls, data, db_session):
        pre_query = db_session.query(Post).filter(Post.timestamp>data['__checkers__']['is_timestamp_present'])
        target_type = data['__checkers__']['is_correct_update_query']['type']
        target = data['__checkers__']['is_correct_update_query']['target']
        if target_type == 'thread':
            query_result = pre_query.filter(Post.to_thread == target)
        elif target_type == 'board':
            query_result = pre_query.filter(Post.board_id == target)
        elif target_type == 'post':
            query_result = pre_query.filter(Post.id == target)
        
        query_result = query_result.limit(data['__config__']['UPDATE_LIMIT'])\
            .from_self()\
            .order_by(Post.timestamp.desc()).all()
        
        return (200, query_result)