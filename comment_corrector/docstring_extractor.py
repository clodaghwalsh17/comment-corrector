from comment_corrector.category import Category
from comment_corrector.comment import Comment
from comment_corrector.python_traversal_utils import PythonTraversalUtils
from comment_corrector.gumtree_subprocess import source_to_tree
import re

class DocstringExtractor:

    def __init__(self, file):
        self.__file = file
        self.__tree = source_to_tree(file)
        self.__docstrings = []

    def extract_docstrings(self):
        self.__search(self.__tree)
        return self.__docstrings
    
    def __search(self, entity):
        if not entity:
            return

        entity_children = entity['children']
        i = 0
       
        while i < len(entity_children):
            entity1 = entity_children[i]

            suite = PythonTraversalUtils.get_suite(entity1['children'])
            if suite is not None:
        
                docstring_node = PythonTraversalUtils.find_docstring_node(suite)
                if docstring_node is not None: 
                    text = docstring_node['children'][0]['label']
                    comment_text = re.sub('[\"\']', '', text).strip()
                    line_number = self.__find_docstring_line_number(text) 
                    length = len(docstring_node['children'][0]['label'])   
                    self.__docstrings.append(Comment(comment_text, line_number, True, real_length=length, category=Category.DOCUMENTATION))
                
                self.__search(suite)                

            i += 1 
    
    def __find_docstring_line_number(self, docstring):
        stripped_docstring = re.sub('[\"\']', '', docstring).strip()
        with open(self.__file) as f:
            line_number = 0
            while True:
                line = f.readline()
                if not line:
                    break

                line_number += 1
                line = line.strip()
                if (docstring.startswith(line) or stripped_docstring.startswith(line)) and self.__relevant_line(line):
                    return line_number 

    def __relevant_line(self, line):
        return line != "" and line != "\"\"\"" and line != "'''"