from ..database import Board, Ban, Post, Captcha
import time
import pickle
from sqlalchemy import and_
from PIL import Image as PIL_Image
import warnings
"""
Policy: on error reject all. Frontend should save the settings beforehand.
"""

warnings.simplefilter('error', PIL_Image.DecompressionBombWarning)

def is_ext_policy_nonconsistent(data, db_session):

    def proper_format_naming(ext):
        return {
            "jpg":"jpeg"
        }.get(ext.lower(), ext.lower())

    def check_extension(ext):
        for i in ['picture', 'sound', 'video']:
            if ext['extension'] in data['__config__']['ALLOWED_EXTENSIONS'].get(i, []):
                return (i, True)
        return (None, False)

    errors, extensions = [], {}
    for i, j in data['__files__'].items():
        #check if the extension is not in allowed
        extensions[i] = {"extension": proper_format_naming(j.filename.rpartition('.')[-1])}
        check_result = check_extension(extensions[i])
        extensions[i]['mediatype'] = check_result[0]
        print(extensions[i])
        if not check_result[1]:
            errors.append(str(i))
    if not errors:
        return (None, extensions)
    else:
        return (415, "Wrong extension(s)", errors)

def is_actual_image(data, db_session):
    errors, images = [], {}
    
    for i, j in data['__files__'].items():
        #every error should be logged so
        #try:

        images[i] = PIL_Image.open(j.stream)
        pass
        #except IOError:
            #errors.append("Unsupported format: %s"%str(i))
        #except PIL_Image.DecompressionBombWarning:
            #errors.append("Decompression bomb?: %s"%str(i))
    if not errors:
        return (None, images)
    else:
        return (415, "Filestream reading exception(s)", errors)