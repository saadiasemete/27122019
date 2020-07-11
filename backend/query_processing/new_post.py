from ..database import Board, Ban, Post, Captcha, Attachment
import time
from sqlalchemy import and_
from . import post_checks, query_processor, attachment_checks
import os

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
            "condition": lambda data, db_session: not post_checks.is_thread(data, db_session),
        },
        {
            "checker": post_checks.is_board_rule_violated,
        },
        {
            "checker": attachment_checks.is_ext_policy_nonconsistent,
        },
        {
            "checker": attachment_checks.is_actual_image,
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
        data['__data__']['sage'] = cls.convert_misrepresented_booleans(data['__data__'].get('sage', False))
        return data
    
    @classmethod
    def save_attachments(cls, data, post_id, db_session):
        def generate_path(filetype, filename, fileformat):
            return ".".join(
               [ os.path.join(
                os.getcwd(),
                data['__config__']['PATH']['__PREFIX__'],
                data['__config__']['PATH'][filetype],
                filename
            ),
            fileformat
            ]
            )
            

        data['thumbnail']  = []
        
        for i, j in data['__checkers__'].get('is_ext_policy_nonconsistent', {}).items():
            if j['mediatype'] == 'picture':
                file_to_save = data['__checkers__']['is_actual_image'][i]
                thumbnail = file_to_save.copy()
                thumbnail.thumbnail(data['__config__']['THUMBNAIL_SIZE'])
                #how do we tell the id otherwise
                new_attachment = Attachment(
                        mediatype = j['mediatype'],
                        extension = j['extension'],
                        post_id = post_id,
                    )
                db_session.add(new_attachment)
                db_session.flush()
                thumbnail.save(
                    generate_path("THUMBNAIL", str(new_attachment.id),j['extension']),
                    format = j['extension'],
                )
                file_to_save.save(
                    generate_path("PICTURE", str(new_attachment.id),j['extension']),
                    format = j['extension'],
                )
            #TODO: other filetypes
            

        for i, j in data['__checkers__'].get('is_actual_image', {}).items():
            data['thumbnail'].append(j.thumbnail(data['__config__']['THUMBNAIL_SIZE']))
        
    
    @classmethod
    def on_checks_passed(cls, data, db_session):
        """
        TODO: permit autofill of board_id if to_thread is specified
        Assumes that the post is legit to be posted.
        """
        is_thread = post_checks.is_thread(data, db_session)
        data = cls.apply_transformations(data, db_session)
        new_post = Post(
            board_id = data['__data__']['board_id'],
            to_thread = data['__data__'].get('to_thread'),
            reply_to = data['__data__'].get('reply_to') if not is_thread else None,
            ip_address = data['__data__']['ip_address'],
            title = data['__data__'].get('title'),
            text  = data['__data__'].get('text'),
            #tripcode = data['__data__'].get('tripcode'),
            #password = data['__data__'].get('password'),
            sage = bool(data['__data__'].get('sage')),
            timestamp = data['__data__']['timestamp'],
        )
        db_session.add(new_post)
        db_session.flush()
        cls.save_attachments(data, new_post.id, db_session)
        if post_checks.is_thread(data, db_session):
            new_post.timestamp_last_bump = data['__data__']['timestamp']
        else:
            if not data['__data__'].get('sage'):
                db_session.query(Post).filter(Post.id == data['__data__']['to_thread']).first().timestamp_last_bump = data['__data__']['timestamp'] 
        db_session.commit()
        return (201, new_post)