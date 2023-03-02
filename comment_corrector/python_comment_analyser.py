from comment_corrector.comment_analyser import CommentAnalyser
from comment_corrector.category import Category
from comment_corrector.utils import Utils
import math

class PythonCommentAnalyser(CommentAnalyser):

    def __init__(self, files):   
        super().__init__(files, Utils.get_code_word_regexes("Python"), Utils.get_terminator("Python"))               

    def _outdated_analysis(self, entity):
        if not entity:
            return

        if self._comment_index >= len(self._comments):
            return

        entity_children = entity['children']

        if self.__introductory_comment(entity):
            # Various types of "comments" may appear before the body of the code
            # These may include combinations of shebang, encoding, documentation comment, copyright comment, header comment or task comment
            occupied_space = 0 
            # Q if copyright not outdated, doc comment could be, any other type could be
            while occupied_space + self._current_comment.real_length() <= int(entity['pos']):
                # wont actually work exactly how is
                # if self._is_copyright_comment(self._current_comment.text()):
                #     self._check_comment()
                               
                occupied_space += self._current_comment.real_length()
                # TODO for some of these do check_relevance else just do check_comment     
                self._check_comment()
        
        # Q needed anymore
        if self.__comment_at_root(entity, entity_children[0]):
            print("Root found")
            self._check_relevance(int(entity['pos']))

        i = 0
        while i < len(entity_children) and self._comment_index < len(self._comments):
            self.__match_comment(entity_children[i], entity_children[i-1])

            # Recursively call match for all suites of the child
            # The suite holds the main body of code for structures such as classes, functions, for loops, while loops and if statements
            children = entity_children[i]['children']
            suites_indexes = self.__find_suite_indexes(children)

            if suites_indexes:
                for suite_index in suites_indexes:
                    self._outdated_analysis(children[suite_index])
            
            i += 1
            
    def __match_comment(self, entity1, entity2):
        # Q do need to do something diff for inline
        if self.__suitable_comment_gap(entity1, entity2) or self.__has_inline_comment(entity1):
            self._check_relevance(int(entity1['pos']))
    
    def __suitable_comment_gap(self, current_entity, previous_entity):
        return (int(current_entity['pos']) - (int(previous_entity['pos']) + int(previous_entity['length']))) >= self._current_comment.length() 

    def __has_inline_comment(self, entity):    
        last_child = self.__find_last_child(entity)
        return ((int(entity['pos']) + int(entity['length'])) - (int(last_child['pos']) + int(last_child['length']))) >= self._current_comment.length() 

    def __comment_at_root(self, root, first_child): 
        return (int(first_child['pos']) - int(root['pos'])) > math.ceil(self._current_comment.length() * 1.35)

    def __introductory_comment(self, entity): # Q could move to abstract class
        return entity['type'] == 'file_input' and entity['pos'] != 0

    def __find_last_child(self, entity):
        if not entity:
            return
        
        stack = []
        stack.append(entity)

        while len(stack) > 0:
            root = stack.pop()

            if not root['children']:
                return root
            else:
                children = root['children']
                stack.append(children[len(children)-1])
    
    def __find_suite_indexes(self, entity):
        indexes = []
        for index, sub_entity in enumerate(entity):
            if sub_entity['type'] == "suite":
                indexes.append(index)
        return indexes    