from ..database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
from . import post_checks, query_processor, utils

class FetchBoards(query_processor.QueryProcessor):
    checkers = [
        {
            "checker": post_checks.is_invalid_data,
        },
    ]

    @classmethod
    def on_checks_passed(cls, data, db_session):
        pre_query = db_session.query(Board)
        order = Board.address.desc()
        query_result = pre_query.order_by(order).all()
        result = query_result
        return (200, result)