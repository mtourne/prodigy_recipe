import os
import base64
import mimetypes

def img_to_data(path):
    """Convert a file (specified by a path) into a data URI."""
    if not os.path.exists(path):
        raise FileNotFoundError
    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as fp:
        data = fp.read()
        data64 = b''.join(base64.encodestring(data).splitlines())
        return 'data:{};base64,{}'.format(mime, data64.decode("utf-8"))
