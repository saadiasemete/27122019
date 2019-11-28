from new_board import SubmitBoard
import time
from sqlalchemy import create_engine
from backend import read_db_engine

def create_board(
    app,
    name = 'test_board',
    description = 'test_description',
    address = 'test_board',
):
    SubmitBoard.process(
        data = {
            'name': name,
            'description': description,
            'address': address,
            'timestamp': int(time.time()),

        },
        db_session = app.session_generator(
            bind = create_engine(read_db_engine(app.config), echo=True)
        )
    )