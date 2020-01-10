
from .tests import qa_utilities, unittests
from .backend.query_processing import SubmitPost

res = unittests.CreateNewThreadNoTripCyrillic()()
print(res.errors)
print("test end")