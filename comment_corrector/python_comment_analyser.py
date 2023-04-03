from comment_corrector.comment_analyser import CommentAnalyser
from comment_corrector.category import Category
from comment_corrector.utils import Utils

class PythonCommentAnalyser(CommentAnalyser):

    def __init__(self, files):   
        super().__init__(files, Utils.get_code_word_regexes("Python"), Utils.get_terminator("Python"))               

    def _outdated_analysis(self, entity):
        if not entity:
            return

        if self._comment_index >= len(self._comments):
            return

        entity_children = entity['children']
        i = 0

        if self.__introductory_comment(entity):
            # Various types of "comments" may appear before the body of the code
            # These may include combinations of shebang, encoding, documentation comment, copyright comment, header comment or task comment
            occupied_space = 0 
            while occupied_space + self._current_comment.real_length() <= int(entity['pos']):
                occupied_space += self._current_comment.real_length()

                if self._is_copyright_comment(self._current_comment.text()):
                    self._check_comment()
                elif self._current_comment.category() == Category.DOCUMENTATION:
                    self._check_comment()                    
                elif self._current_comment.category() == Category.UNTRACKABLE:
                    self._next_comment()
                else:
                    suite_indexes = self.__find_suite_indexes(entity_children)
                    # Found a comment describing a script or a line of code at the beginning of the file
                    if len(suite_indexes) == 0:
                        self._check_relevance(entity_children[0])
                    # Account for class definition or function definition at beginning of file
                    else:
                        self._check_relevance(entity)
        
        while i < len(entity_children) and self._comment_index < len(self._comments):
            entity1 = entity_children[i]
            entity2 = entity_children[i-1]
            if self.__suitable_comment_gap(entity1, entity2) or self.__has_inline_comment(entity1):
                self._check_relevance(entity1)

            # Recursively call match for all suites of the child
            # The suite holds the main body of code for structures such as classes, functions, for loops, while loops and if statements
            children = entity_children[i]['children']
            suite_indexes = self.__find_suite_indexes(children)

            if suite_indexes:
                for suite_index in suite_indexes:
                    self._outdated_analysis(children[suite_index])
            
            i += 1
    
    def _is_comment_editing_action(self, action, entity): 
        if entity['type'] == "funcdef":
            return self.__function_affects_comment(action, entity)            
        else:
            return self.__statement_affects_comment(action, entity)
    
    def __statement_affects_comment(self, action, entity):
        file_position = int(entity['pos'])
        reference_point = file_position + int(entity['length'])
        if action.type() == "update-node" and file_position <= action.src_start() and action.src_start() <= reference_point:
            return True
        elif action.type() == "insert-node" and file_position == action.dst_start():
            return True
        elif action.type() == "move-tree" and file_position == action.src_start() and action.src_end() < self._eof:
            return True
        elif action.type() == "move-tree" and file_position == action.dst_start() and action.dst_end() < self._eof:
            return True
        elif action.type() == "delete-tree" and file_position == action.src_start():
            return True
        
        return False

    def __function_affects_comment(self, action, entity):
        if action.affects_function(): 
            return True
        
        name_node = self.__find_fn_name_node(entity['children'])
        name_node_start = int(name_node['pos'])
        name_node_end = name_node_start + int(name_node['length'])

        if action.type() == "update-node" and name_node_start <= action.src_start() and action.src_start() <= name_node_end:
            return True

        # A function may become outdated if the parameters to it change
        param_node = self.__find_fn_param_node(entity['children'])
        if param_node is not None:
            param_node_start = int(param_node['pos'])
            param_node_end = param_node_start + int(param_node['length'])
                            
            if action.type() == "update-node" and param_node_start <= action.src_start() and action.src_start() <= param_node_end:
                return True
        
        # If the function has a return statement check if any modifications were made to it
        return_node = self.__find_return_node(entity['children'])
        if return_node is not None:
            return_node_start = int(return_node['pos'])
            return_node_end = return_node_start + int(return_node['length'])
            
            if action.type() == "update-node" and return_node_start <= action.src_start() and action.src_start() <= return_node_end:
                return True
            elif action.type() == "insert-node" and return_node_start <= action.dst_start() and action.dst_start() <= return_node_end:
                return True
        
        return False
               
    def __suitable_comment_gap(self, current_entity, previous_entity):
        return (int(current_entity['pos']) - (int(previous_entity['pos']) + int(previous_entity['length']))) >= self._current_comment.length() 

    def __has_inline_comment(self, entity):    
        last_child = self.__find_last_child(entity)
        return ((int(entity['pos']) + int(entity['length'])) - (int(last_child['pos']) + int(last_child['length']))) >= self._current_comment.length() 

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
    
    def __find_return_node(self, entity):
        suite_indexes = self.__find_suite_indexes(entity)
        if len(suite_indexes) == 1:
            sub_entities = entity[suite_indexes[0]]['children']

            for sub_entity in sub_entities:
                if not sub_entity:
                    return
                
                stack = []
                stack.append(sub_entity)

                while len(stack) > 0:
                    root = stack.pop()

                    if root['type'] == "return_stmt":
                        return root
                    else:
                        children = root['children']
                        for child in children:
                            stack.append(child)
    
    def __find_fn_param_node(self, entity):
        for sub_entity in entity:
            if sub_entity['type'] == "parameters":
                return sub_entity
    
    def __find_fn_name_node(self, entity):
        for sub_entity in entity:
            if sub_entity['type'] == "name":
                return sub_entity