from comment_parser import comment_parser
import os
import sys

MIME_MAPPING =  {
    '.java' : 'text/x-java-source',
    '.py' : 'text/x-python',
    # The MIME type text/x-c operates on both .c and .h files
    '.c' : 'text/x-c',
    '.h' : 'text/x-c',
    '.js' : 'application/javascript'
}

def list_comments(file):
    try:
        mime = get_mime_type(file)
        return comment_parser.extract_comments(file, mime)
    except Exception as e:
        print(e)  
        sys.exit()

def get_mime_type(file):
    _, extension = os.path.splitext(file)
    if MIME_MAPPING.get(extension) is not None:
        return MIME_MAPPING.get(extension)
    else:
        raise Exception("This file type is not supported")