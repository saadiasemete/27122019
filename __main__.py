
from .tests import qa_utilities, unittests
from .backend.query_processing import SubmitPost
import json

unittests.CreateNewThreadNoTripCyrillic()()
unittests.CreateThreadWithNoImage()()
unittests.PostingInThreadNoImage()()
unittests.ThreadBump()()
unittests.ThreadSage()()
unittests.ListThreads()()
unittests.ListPostsInUnistream()()
unittests.CheckPostUpdates()()