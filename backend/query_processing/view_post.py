from ..database import Board, Ban, Post, Captcha, Attachment
import time
from sqlalchemy import and_
from . import post_checks, query_processor

class OpenPost(query_processor.QueryProcessor):
    checkers = [
        {
            "checker": post_checks.is_invalid_data,
        },
        #{
        #    "checker": post_checks.is_board_inexistent,
        #},
        #{
        #    "checker": is_thread_inexistent,
        #},
    ]

    @classmethod
    def on_checks_passed(cls, data, db_session):
        """
        For now - let us open a single post, then will see.
        """
        #fetched_post = db_session.query(Post, Attachment).filter(Post.id == data['__data__']['post_id'])\
        #    .outerjoin(Attachment).all()
        
        fetched_post = db_session.query(Post).outerjoin(Attachment)\
        .filter(Post.id == data['__data__']['post_id']).all()
        


        #fetched_post = db_session.query(Post, Attachment).filter(Post.id == data['__data__']['post_id'])\
        #    .filter(Attachment.post_id == Post.id).all()
        if fetched_post:
            return (200, fetched_post)
        else:
            return (404, "Post with that ID is not found")