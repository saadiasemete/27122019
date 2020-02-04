from ..database import Board, Ban, Post, Captcha
import time
from sqlalchemy import and_
import PIL
import warnings
"""
Policy: on error reject all. Frontend should save the settings beforehand.
"""

warnings.simplefilter('error', PIL.Image.DecompressionBombWarning)

def is_ext_policy_nonconsistent(data, db_session):
    errors, extensions = [], {}
    for i, j in data['__files__'].values():
        #check if the extension is not in allowed
        extensions[i] = j.filename.rpartition('.')[-1]
        if extensions[i] not in data['__config__']['ALLOWED_EXTENSIONS']:
            errors.append(str(i))
    if not errors:
        return (None, extensions)
    else:
        return (415, "Wrong extension(s)", errors)

def is_actual_image(data, db_session):
    errors, images = [], {}
    
    for i, j in data['__files__'].values():
        #every error should be logged so
        try:
            images[i] = PIL.Image.open(j.stream)
        except IOError:
            errors.append("Unsupported format: %s"%str(i))
        except PIL.Image.DecompressionBombWarning:
            errors.append("Decompression bomb?: %s"%str(i))
    if not errors:
        return (None, images)
    else:
        return (415, "Filestream reading exception(s)", errors)