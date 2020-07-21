from ..database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
from . import post_checks, query_processor, utils

class Pagination(query_processor.QueryProcessor):
    """
    I've decided to make it all one method,
    as it must be uniform by design.
    """
    checkers = [
        {
            "checker": post_checks.is_invalid_data,
        },
        {
            "checker": post_checks.is_correct_update_pagination_query,
        },
        {
            "checker": post_checks.is_thread_inexistent,
            "condition": lambda data, db_session: data['__checkers__']['is_correct_update_pagination_query']['type']=='thread',
            "args": ['thread_id']
        },
        {
            "checker": post_checks.is_board_inexistent,
            "condition": lambda data, db_session: data['__checkers__']['is_correct_update_pagination_query']['type']=='board',
        },
        {
            "checker": post_checks.is_post_inexistent,
            "condition": lambda data, db_session: data['__checkers__']['is_correct_update_pagination_query']['type']=='post',
            "args": ['post_id']
        },
    ]

    @classmethod
    def pagination_preprocessing(cls, data, db_session, threads):
        return utils.pagination(
            page_length = data['__config__']['BOARD_PAGE_LENGTH'],
            preview_length = data['__config__']['THREAD_PREVIEW_LENGTH'],
            posts = threads,
            page = data['__data__'].get('page', 1)
        )

    @classmethod
    def on_checks_passed(cls, data, db_session):
        pre_query = db_session.query(Post)
        target_type = data['__checkers__']['is_correct_update_pagination_query']['type']
        target = data['__checkers__']['is_correct_update_pagination_query']['target']
        order = Post.timestamp.desc()
        if target_type == 'thread':
            query_result = pre_query.filter(Post.to_thread == target)
        elif target_type == 'board':
            query_result = pre_query.filter(Post.board_id == target, Post.to_thread == 0)
            order = Post.timestamp_last_bump.desc()
        elif target_type == 'post':
            query_result = pre_query.filter(Post.reply_to == target)
        elif target_type == 'unistream':
            query_result = pre_query
            
        query_result = query_result.limit(data['__config__']['UPDATE_LIMIT'])\
            .from_self()\
            .order_by(order).all()
        result = cls.pagination_preprocessing(data, db_session, query_result)
        return (200, result)