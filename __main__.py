
from .tests import qa_utilities, unittests
from .backend.query_processing import SubmitPost
import json

res = unittests.CreateNewThreadNoTripCyrillic()()
#print(res.errors)
print(len(res.errors))
try:
    with open("test_error_log.txt", "w", encoding="utf-8") as f:
        f.write(res.errors[0][1])
except:
    pass
print("test end")