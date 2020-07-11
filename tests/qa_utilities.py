from ..backend.query_processing import SubmitBoard, SubmitPost
import time, os
from sqlalchemy import create_engine
from ..backend.blueprint import read_db_engine
from PIL import Image as PIL_Image

def create_board(
    app,
    name = 'test_board',
    description = 'test_description',
    address = 'test_board',
):
    print(" here goes nothing ")
    a = SubmitBoard.process(
        data = {'__data__':{
            'name': name,
            'description': description,
            'address': address,


        }},
        db_session = app.session_generator(
            #bind = create_engine(read_db_engine(app.config), echo=True)
            
            bind = app.sql_engine
        )
    )
    print(a)

def create_thread(
    app,
    title = 'test_thread',
    text = 'test_text',
    board_id = 1,
    ip_address = "127.0.0.1",
):
    """
    Note that this function circumvents attachments rules.
    """
    print(" here goes nothing ")
    a = SubmitPost.process(
        data = {'__data__':{
            'board_id': board_id,
            'reply_to': None,
            'title': title,
            'text': text,
            
            'ip_address': "127.0.0.1",

        }},
        db_session = app.session_generator(
            #bind = create_engine(read_db_engine(app.config), echo=True)
            
            bind = app.sql_engine
        ),
        testing_mode=True
    )
    print(a)

def prepare_image(image_path = None):
    if not image_path:
        image_path = os.path.join('pyexaba', 'tests', 'test_image.jpg')
    #with PIL_Image.open(image_path, mode = 'rb') as f:
        #image = PIL_Image(f).to_bytes()
        #image = f.tobytes()
    #return image
    return open(image_path, mode = "rb")