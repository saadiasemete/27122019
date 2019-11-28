import unittest
#from backend_client import Client as test_client
from backend import generate_app
import json
from qa_utilities import create_board

NEW_BOARD = "/api/new_board"
NEW_POST = "/api/new_post"
VIEW_POST = "/api/post"

class PostingAndViewing(unittest.TestCase):
    def setUp(self):
        self.FlaskApp = generate_app("testing_cfg.json")
        self.FlaskApp.run(debug = self.FlaskApp.config['DEBUG'], testing = True)
        self.TestClient = self.FlaskApp.test_client()
        create_board(self.FlaskApp)
        self.OwnDataset = json.load(open("unittests_dataset.json", encoding="utf-8"), encoding="utf-8")[self.__class__.__name__]
    
    def CreateNewThreadNoTripCyrillic(self):
        """
        As we assume it to be usable by citizens of the CIS.
        STOP. You should be able to get the post_id from the request. Do it.
        """
        ThisData = self.OwnDataset['CreateNewThreadNoTripCyrillic']
        #let's see how it works
        post_result = self.TestClient.post(NEW_POST, json = ThisData, as_tuple = True)[1]
        post_viewed = self.TestClient.get(VIEW_POST, params = {"post_id":post_result['data']['post_id']}, as_tuple = True)[1]
        #checking if it exists at all
        self.assertTrue(post_viewed['result'], "No post detected")
        #checking that no data is lost during conversion
        for i in [
            'board_id',
            'to_thread',
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