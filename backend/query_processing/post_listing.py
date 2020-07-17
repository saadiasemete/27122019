from ..database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
from . import post_checks, query_processor, utils

class PostListing(query_processor.QueryProcessor):
    checkers = [
        {
            "checker": post_checks.is_invalid_data,
        },
        #{
        #    "checker": is_thread_inexistent,
        #},
    ]

    @classmethod
    def threads_preprocessing(cls, data, db_session, threads):
        return utils.pagination(
            page_length = data['__config__']['UNISTREAM_PAGE_LENGTH'],
            preview_length = data['__config__']['UNISTREAM_POST_PREVIEW_LENGTH'],
            posts = threads,
            page = data['__data__'].get('page', 1)
        )

    @classmethod
    def on_checks_passed(cls, data, db_session):
        threads = db_session.query(Post).order_by(Post.timestamp.desc()).all()
        threads = cls.threads_preprocessing(data, db_session, threads)
        return (200, threads)