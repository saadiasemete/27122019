import unittest
#from backend_client import Client as test_client
from ..backend.app import generate_app
import json
from .qa_utilities import create_board, prepare_image, create_thread
import os
import requests
import io
import time

NEW_BOARD = "/api/new_board"
NEW_POST = "/api/new_post"
VIEW_POST = "/api/view_post"
PAGINATION = "/api/pagination"
GET_UPDATES = "/api/get_updates"

class PostingAndViewing(unittest.TestCase):
    """
    Base for tests intended for posting and viewing
    """
    def create_thread_unsafe(self):
        """
        Is not guaranteed to be created
        if the standard thread creation
        has fallen
        """
        ThisData =dict(
            (('board_id', 1,),
            ('title', "test thread",),
            ('text', "adfsf",),)
        ) #it keeps self-identifying as a tuple otherwise, idk why
        ThisData['files'] = [
            (prepare_image(), 'file1.jpg'),
            (prepare_image(), 'file2.jpg'),
        ]
        return self.TestClient.post(NEW_POST, data = ThisData)


    def setUp(self):
        self.FlaskApp = generate_app("testing_cfg.json")
        self.TestClient = self.FlaskApp.test_client()
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
            self.assertEqual(post_viewed['data'][0][i], ThisData[i], "%s doesn't match"%i)
        self.assertEqual(
            len(post_viewed['data'][0]['attachments']),
            len(ThisData['files']),
            "Different attachment quantity"
        )
        #checking if there is any timestamp
        self.assertTrue(post_viewed['data'][0]['timestamp'])
        #making sure the thread is bumped by its own creation
        self.assertEqual(post_viewed['data'][0]['timestamp'], 
                        post_viewed['data'][0]['timestamp_last_bump'], 
                        "The thread has been created but not self-bumped")

class CreateThreadWithNoImage(PostingAndViewing):
    def runTest(self):
        """
        As we assume it to be usable by citizens of the CIS.
        STOP. You should be able to get the post_id from the request. Do it.
        """
        ThisData = self.OwnDataset['CreateNewThreadNoTripCyrillic']
        post_request = self.TestClient.post(NEW_POST, data = ThisData)
        post_result = post_request.json
        self.assertEqual(
            post_result['data'],
            "Attachment required",
            "Can create a thread without an image"
            )

class PostingInThreadNoImage(PostingAndViewing):
    def runTest(self):
        #create_thread(self.FlaskApp)

        ThisData = self.OwnDataset['CreateNewThreadNoTripCyrillic']
        ThisData['files'] = [
            (prepare_image(), 'file1.jpg'),
            (prepare_image(), 'file2.jpg'),
        ]
        self.TestClient.post(NEW_POST, data = ThisData)

        ThisData = self.OwnDataset['GenericPost']
        ThisData['board_id'] = ThisData['to_thread'] = 1
        post_request = self.TestClient.post(NEW_POST, data = ThisData)
        post_result = post_request.json
        self.assertTrue(post_result['result'], post_result['data'])
        post_viewed = self.TestClient.get(VIEW_POST, query_string = {"post_id":post_result['data']['id']}).json
        #checking if there is any timestamp
        self.assertTrue(post_viewed['data'][0]['timestamp'])
        for i in [
            'board_id',
            'reply_to',
            'title',
            'text',
            'sage'
        ]:
            self.assertEqual(post_viewed['data'][0][i], ThisData[i], "%s doesn't match"%i)
        

class ThreadBump(PostingAndViewing):
    def runTest(self):
        create_thread(self.FlaskApp)
        ThisData = self.OwnDataset['GenericPost']
        ThisData['board_id'] = ThisData['to_thread'] = 1
        post_request = self.TestClient.post(NEW_POST, data = ThisData)
        post_viewed = self.TestClient.get(VIEW_POST, query_string = {"post_id":1}).json
        self.assertNotEqual(post_viewed['data'][0]['timestamp'], 
                        post_viewed['data'][0]['timestamp_last_bump'], 
                        "Bump failed")

class ThreadSage(PostingAndViewing):
    def runTest(self):
        create_thread(self.FlaskApp)
        ThisData = self.OwnDataset['GenericPost']
        ThisData['board_id'] = ThisData['to_thread'] = 1
        ThisData['sage'] = True
        post_request = self.TestClient.post(NEW_POST, data = ThisData)
        post_viewed = self.TestClient.get(VIEW_POST, query_string = {"post_id":1}).json
        self.assertEqual(post_viewed['data'][0]['timestamp'], 
                        post_viewed['data'][0]['timestamp_last_bump'], 
                        "Sage failed")

class ListThreads(PostingAndViewing):
    def runTest(self):
        length = int(self.FlaskApp.config['BOARD_PAGE_LENGTH']*1.5)
        for i in range(length):
            self.create_thread_unsafe()
        board_viewed = self.TestClient.get(PAGINATION, query_string = {"board_id":1}).json
        self.assertEqual(len(board_viewed['data']['posts_current_page']), 
                        self.FlaskApp.config['BOARD_PAGE_LENGTH'], 
                        "Issue with the first page")
        board_viewed = self.TestClient.get(PAGINATION, query_string = {"board_id":1, "page":2}).json
        self.assertEqual(len(board_viewed['data']['posts_current_page']), 
                        length-self.FlaskApp.config['BOARD_PAGE_LENGTH'], 
                        "Issue with the remaining posts")

class ListPostsInUnistream(PostingAndViewing):
    def runTest(self):
        length = int(self.FlaskApp.config['UNISTREAM_PAGE_LENGTH']*1.5)
        for i in range(length):
            self.create_thread_unsafe()
        board_viewed = self.TestClient.get(PAGINATION).json
        self.assertEqual(len(board_viewed['data']['posts_current_page']), 
                        self.FlaskApp.config['UNISTREAM_PAGE_LENGTH'], 
                        "Issue with the first page")
        board_viewed = self.TestClient.get(PAGINATION, query_string = {"page":2}).json
        self.assertEqual(len(board_viewed['data']['posts_current_page']), 
                        length-self.FlaskApp.config['UNISTREAM_PAGE_LENGTH'], 
                        "Issue with the remaining posts")

class CheckPostUpdates(PostingAndViewing):
    def runTest(self):
        """
        Need to get this stuff done
        """
        timestamp = time.time()
        length = int(self.FlaskApp.config['UPDATE_LIMIT']*1.5)
        for i in range(length):
            self.create_thread_unsafe()
        board_viewed = self.TestClient.get(GET_UPDATES, query_string = {"board_id":1, "timestamp": timestamp}).json
        self.assertEqual(len(board_viewed['data']), 
                        self.FlaskApp.config['UPDATE_LIMIT'], 
                        "Issue with the length of updates in board view")
        for i in range(length):
            self.create_thread_unsafe()
        timestamp = board_viewed['data'][0]['timestamp']
        unistream_viewed = self.TestClient.get(GET_UPDATES, query_string = {"timestamp": timestamp}).json
        self.assertEqual(len(unistream_viewed['data']), 
                        self.FlaskApp.config['UPDATE_LIMIT'], 
                        "Issue with the length of updates in unistream")
        
        