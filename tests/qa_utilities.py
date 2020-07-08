from ..backend.query_processing import SubmitBoard
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
            'timestamp': int(time.time()),

        }},
        db_session = app.session_generator(
            #bind = create_engine(read_db_engine(app.config), echo=True)
            
            bind = app.sql_engine
        )
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