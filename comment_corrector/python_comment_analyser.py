from comment_corrector.comment_analyser import CommentAnalyser
from comment_corrector.category import Category
from comment_corrector.utils import Utils
from comment_corrector.python_traversal_utils import PythonTraversalUtils

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
            current_comment = self._get_current_comment()
            while occupied_space + current_comment.real_length() <= int(entity['pos']):
                occupied_space += current_comment.real_length()

                if self._is_copyright_comment(current_comment.text()):
                    self._check_comment()                  
                elif current_comment.category() == Category.UNTRACKABLE:
                    self._next_comment()
                else:
                    self._check_relevance(entity_children[0])
        
        while i < len(entity_children) and self._comment_index < len(self._comments):
            entity1 = entity_children[i]
            entity2 = entity_children[i-1]

            if self.__suitable_comment_gap(entity1, entity2) or self.__has_inline_comment(entity1):
                self._check_relevance(entity1)
            
            # Check if the current entity contains a suite
            # Call outdated_analysis recursively for every suite of the tree
            # The suite holds the main body of code for structures such as classes, functions, for loops, while loops and if statements
            suite = PythonTraversalUtils.get_suite(entity1['children'])
            if suite is not None:
                docstring_node = PythonTraversalUtils.find_docstring_node(suite)
                if docstring_node is not None:  
                    self._check_relevance(entity1)
                
                if entity1['type'] == "if_stmt":
                    suite_indexes = PythonTraversalUtils.find_suite_indexes(entity1['children'])
                    for suite_index in suite_indexes:
                        if self.__comment_inside_suite(entity1['children'][suite_index]):
                            self._check_relevance(entity1['children'][suite_index]['children'][0])
                elif self.__comment_inside_suite(suite):
                    if entity1['type'] == "classdef":
                        self._check_relevance(entity1)
                    elif entity1['type'] == "funcdef":
                        if suite['children']:
                            self._check_relevance(suite['children'][0]) 
                        else:
                            self._check_relevance(entity1)
                    elif entity1['type'] in ["for_stmt", "while_stmt"] and suite['children']: 
                        self._check_relevance(suite['children'][0]) 

                self._outdated_analysis(suite)                

            i += 1
    
    def _is_comment_editing_action(self, action, entity): 
        if entity['type'] == "classdef":
            return self.__class_affects_comment(action, entity)
        elif entity['type'] == "funcdef":
            return self.__function_affects_comment(action, entity)  
        elif entity['type'] == "if_stmt":
            return self.__if_stmt_affects_comment(action, entity)
        elif entity['type'] in ["for_stmt", "while_stmt"]:
            return self.__iteration_construct_affects_comment(action, entity)
        else:
            return self.__statement_affects_comment(action, entity)
    
    def __statement_affects_comment(self, action, entity):
        file_position = int(entity['pos'])
        reference_point = file_position + int(entity['length'])
        if action.type() == "update-node" and file_position <= action.src_start() and action.src_start() <= reference_point:
            return True
        elif action.type() == "insert-node" and file_position == action.dst_start():
            return True
        elif action.type() == "move-tree" and file_position == action.src_start() and action.src_end() <= self._eof:
            return True
        elif action.type() == "move-tree" and file_position == action.dst_start() and action.dst_end() <= self._eof:
            return True
        elif action.type() == "delete-tree" and file_position == action.src_start():
            return True
        
        return False

    def __function_affects_comment(self, action, entity):
        if self.__current_fn_affected(action, entity):
            return True

        if self.__renamed_body(action, entity):
            return True

        # A function may become outdated if the parameters to it change   
        if self.__fn_parameter_modified(action, entity):
            return True
        
        # A function is likely outdated if the pass keyword is replaced by actual logic
        suite = PythonTraversalUtils.get_suite(entity['children'])
        if action.type() == "insert-tree" and len(suite['children']) == 0 and int(suite['pos']) == action.dst_start():
            return True
        
        # If the function has a return statement check if any modifications were made to it
        return_node = PythonTraversalUtils.find_return_node(entity['children'])
        if return_node is not None:
            return_node_start = int(return_node['pos'])
            return_node_end = return_node_start + int(return_node['length'])
            
            if action.type() == "update-node" and return_node_start <= action.src_start() and action.src_start() <= return_node_end:
                return True
            elif action.type() == "insert-node" and return_node_start <= action.dst_start() and action.dst_start() <= return_node_end:
                return True
        
        return False
    
    def __class_affects_comment(self, action, entity):
        if self.__renamed_body(action, entity):
            return True
        
        suite = PythonTraversalUtils.get_suite(entity['children'])
        suite_pos = int(suite['pos'])

        # When the actual logic for the class is implemented rather than having a pass statement the class comment might need to be reviewed
        if action.type() == "insert-node" and len(suite['children']) == 0 and suite_pos == action.src_start():
            return True
        
        # Changes to the inheritance hierarchy of a class may impact the class comment
        if int(entity['pos']) <= action.src_start() and action.src_start() <= suite_pos:
            return True

        # A change to the constructor might cause the class comment to become outdated 
        constructor = PythonTraversalUtils.get_constructor(entity)
        if constructor is not None: 
            if self.__current_fn_affected(action, constructor):
                return True        

            if self.__fn_parameter_modified(action, constructor):
                return True
        
        # If the class attributes are modified the associated class comment may become outdated
        if suite['children']:
            first_class_entity = PythonTraversalUtils.get_first_class_entity(suite)
            # Case where modify existing class attributes
            if first_class_entity['type'] != "funcdef":
                if int(first_class_entity['pos']) <= action.src_start() and action.src_start() <= int(first_class_entity['pos']) + int(first_class_entity['length']):
                    return True
            # Case where introduce class attributes
            elif action.type() == "insert-tree" and first_class_entity['type'] == "funcdef" and action.src_start() < int(first_class_entity['pos']):
                return True
        
        return False

    def __if_stmt_affects_comment(self, action, entity):
        suite_indexes = PythonTraversalUtils.find_suite_indexes(entity['children'])
        for suite_index in suite_indexes:
            if_suite = entity['children'][suite_index]
            
            if suite_index - 1 >= 0 and entity['children'][suite_index-1]['type'] != "suite":
                if_condition = entity['children'][suite_index-1]
                # Case where clauses of if statement are modified
                if int(if_condition['pos']) <= action.src_start() and action.src_start() <= int(if_suite['pos']):
                    return True
                
            # Case where add new clauses to the if statement
            if action.type() == "insert-tree" and action.dst_end() <= int(if_suite['pos']) + int(if_suite['length']):
                return True           
        
        return False        
    
    def __iteration_construct_affects_comment(self, action, entity):
        suite = PythonTraversalUtils.get_suite(entity['children'])
        suite_pos = int(suite['pos'])
        
        # A change to the iteration condition may cause the comment to be outdated
        if int(entity['pos']) <= action.src_start() and action.src_start() <= suite_pos: 
            return True
        
        if action.type() == "insert-tree" and len(suite['children']) == 0 and action.dst_start() == suite_pos:
            return True     
        
        return False
    
    def __suitable_comment_gap(self, current_entity, previous_entity):
        return (int(current_entity['pos']) - (int(previous_entity['pos']) + int(previous_entity['length']))) >= self._get_current_comment().real_length() 

    def __has_inline_comment(self, entity): 
        last_child = PythonTraversalUtils.find_last_child(entity)
        return ((int(entity['pos']) + int(entity['length'])) - (int(last_child['pos']) + int(last_child['length']))) >= self._get_current_comment().length() 

    def __introductory_comment(self, entity): 
        return entity['type'] == 'file_input' and entity['pos'] != 0

    def __comment_inside_suite(self, suite):
        if suite['children']:
            return int(suite['children'][0]['pos']) - int(suite['pos']) >= self._get_current_comment().real_length() 
        else:
            return int(suite['length']) >= self._get_current_comment().real_length()   
    
    def __renamed_body(self, action, entity):
        name_node = PythonTraversalUtils.find_name_node(entity['children'])
        name_node_start = int(name_node['pos'])
        name_node_end = name_node_start + int(name_node['length'])
        return action.type() == "update-node" and name_node_start <= action.src_start() and action.src_start() <= name_node_end

    def __fn_parameter_modified(self, action, fn):
        fn_params = PythonTraversalUtils.get_function_params(fn['children'])
        fn_body = PythonTraversalUtils.get_suite(fn['children'])
        return int(fn_params['pos']) <= action.src_start() and action.src_start() <= int(fn_body['pos'])

    def __current_fn_affected(self, action, fn):
        return action.affects_function() and int(fn['pos']) <= action.src_start() and action.src_start() <= int(fn['pos']) + int(fn['length'])