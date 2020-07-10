import unittest
#from backend_client import Client as test_client
from ..backend.app import generate_app
import json
from .qa_utilities import create_board, prepare_image
import os
import requests
import io

class custom_test_client():
    """
    Because screw Werkzeug's occult stuff, that's why.
    """
    def __init__(self, address, port):

        self.address = address
        if self.address == "localhost" or self.address == "127.0.0.1":
            self.address = "http://127.0.0.1"
        self.port = str(port)
        self.session = requests.session()
        self.full_address = ":".join([self.address, self.port])
        self.session.get(self.full_address) #initialize the session
    
    def get(self, address, **kwargs):
        url = "".join([self.full_address, address]) #bc must correspond to blueprint
        return self.session.get(url, **kwargs)
    
    def post(self, address, **kwargs):
        url = "".join([self.full_address, address]) #bc must correspond to blueprint
        return self.session.post(url, **kwargs)

NEW_BOARD = "/api/new_board"
NEW_POST = "/api/new_post"
VIEW_POST = "/api/view_post"

class PostingAndViewing(unittest.TestCase):
    """
    Base for tests intended for posting and viewing
    """
    def setUp(self):
        self.FlaskApp = generate_app("testing_cfg.json")
        #self.FlaskApp.run(debug = self.FlaskApp.config['DEBUG'])
        self.TestClient = self.FlaskApp.test_client()
        #we don't know how to include files in it
        #self.TestClient = custom_test_client("localhost", 5000)
        create_board(self.FlaskApp)
        unittests_dataset_path = os.path.join('pyexaba', 'tests', 'unittests_dataset.json')
        self.OwnDataset = json.load(open(unittests_dataset_path, encoding="utf-8"), encoding="utf-8")['PostingAndViewing']

class CreateNewThreadNoTripCyrillic(PostingAndViewing):
    def runTest(self):
        """
        As we assume it to be usable by citizens of the CIS.
        STOP. You should be able to get the post_id from the request. Do it.
        """
        ThisData = self.OwnDataset['CreateNewThreadNoTripCyrillic']
        image = prepare_image()
        #with open("image_data.txt", "wb") as f:
            #f.write(image)
        #let's see how it works
        #post_request = self.TestClient.post(NEW_POST, data = ThisData, files = {'file': image})
        ThisData['files'] = [
            (prepare_image(), 'file1.jpg'),
            (prepare_image(), 'file2.jpg'),
        ]
        post_request = self.TestClient.post(NEW_POST, data = ThisData)
        post_result = post_request.json
        self.assertTrue(post_result['result'], post_result['data'])
        post_viewed = self.TestClient.get(VIEW_POST, query_string = {"post_id":post_result['data']['id']}).json
        #checking if it exists at all
        self.assertTrue(post_viewed['result'], "No post detected")
        #checking that no data is lost during conversion
        for i in [
            'board_id',
            'reply_to',
            'title',
            'text',
            'sage'
            ]:
            self.assertEqual(post_viewed['data'][i], ThisData[i], "%s doesn't match"%i)
        #checking if there is any timestamp
        self.assertTrue(post_viewed['data']['timestamp'])
        #making sure the thread is bumped by its own creation
        self.assertEqual(post_viewed['data']['timestamp'], 
                        post_viewed['data']['timestamp_last_bump'], 
                        "The thread has been created but not self-bumped")