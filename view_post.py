from database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
import post_checks
import query_processor

class OpenPost(query_processor.QueryProcessor):
    checkers = [
        {
            "checker": post_checks.is_invalid_data,
        },
        {
            "checker": post_checks.is_board_inexistent,
        },
        #{
        #    "checker": is_thread_inexistent,
        #},
    ]

    @classmethod
    def view_post(cls, data, db_session):
        """
        For now - let us open a single post, then will see.
        """
        fetched_post = db_session.query(Post).filter(id == data['post_id'])
        if fetched_post:
            return (200, fetched_post)
        else:
            return (404, "Post with that ID is not found")