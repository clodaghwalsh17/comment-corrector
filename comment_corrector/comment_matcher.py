import json
import math

PYTHON_LABELS = {
    "funcdef" : "function_member_comment",
    "expr_stmt" :  "variable_member_comment" 
    # "atom_expr" : member_comment
}

COPYRIGHT_IDENTIFIERS = ["license", "licence", "copyright", "distributed", "warranty"]
TASK_IDENTIFIERS = ["TODO", "FIXME", "FIX", "BUG", "HACK"]

class PythonCommentMatcher():

    def __init__(self, json_str_tree, comments):
        tree = json.loads(json_str_tree)   
        # self.__tree is a dictionary with the keys type, pos, length, children      
        self.__tree = tree['root']
        self.__comments = comments
        self.__comment_index = 0
        self.__current_comment = self.__comments[self.__comment_index]

    def match(self):
        self.__match(self.__tree)
    
    def __match(self, entity):
        if not entity:
            return

        if self.__comment_index >= len(self.__comments):
            return

        entity_children = entity['children']

        if self.__introductory_comment(entity):
            # Various types of "comments" may appear before the body of the code
            # These may include combinations of shebang, encoding, documentation comment, copyright comment, header comment or task comment
            occupied_space = 0 
            while occupied_space + self.__current_comment.real_length() <= int(entity['pos']):
                if self.__current_comment.category() == "":
                    if self.__is_copyright_comment(self.__current_comment.text()):
                        self.__current_comment.categorise_comment("copyright")
                    elif self.__is_task_comment(self.__current_comment.text()):
                        self.__current_comment.categorise_comment("task")
                    else:
                        self.__current_comment.categorise_comment("intro")
                
                print(repr(self.__current_comment))
                occupied_space += self.__current_comment.real_length()
                self.__next_comment()      
  
        if self.__comment_at_root(entity, entity_children[0]):
            if self.__has_inline_comment(entity):
                self.__tag_inline_comment()
            else:
                self.__current_comment.categorise_comment("root")
                print(repr(self.__comments[self.__comment_index]))
                self.__next_comment()

        i = 0
        while i < len(entity_children) and self.__comment_index < len(self.__comments):
            self.__match_comment(entity_children[i], entity_children[i-1])

            # Recursively call match for all suites of the child
            # The suite holds the main body of code for structures such as classes, functions, for loops, while loops and if statements
            children = entity_children[i]['children']
            suites_indexes = self.__find_suite_indexes(children)

            if suites_indexes:
                for suite_index in suites_indexes:
                    self.__match(children[suite_index])
            
            i += 1
            
    def __match_comment(self, entity1, entity2):
        if self.__suitable_comment_gap(entity1, entity2):
            if self.__is_task_comment(self.__current_comment.text()):
                self.__current_comment.categorise_comment("task")
            else:
                # TODO call determine category function
                self.__current_comment.categorise_comment("regular")
                
            print(repr(self.__current_comment))
            self.__next_comment()

        if self.__has_inline_comment(entity1):
            self.__tag_inline_comment()  
  
    def __tag_inline_comment(self):
        if self.__is_task_comment(self.__current_comment.text()):
            self.__current_comment.categorise_comment("inline task")
        else: 
            self.__current_comment.categorise_comment("inline")
        print(repr(self.__current_comment))
        self.__next_comment()
    
    def __suitable_comment_gap(self, current_entity, previous_entity):
        return (int(current_entity['pos']) - (int(previous_entity['pos']) + int(previous_entity['length']))) >= self.__current_comment.length() 

    def __has_inline_comment(self, entity):    
        last_child = self.__find_last_child(entity)
        return ((int(entity['pos']) + int(entity['length'])) - (int(last_child['pos']) + int(last_child['length']))) >= self.__current_comment.length() 

    def __comment_at_root(self, root, first_child): 
        return (int(first_child['pos']) - int(root['pos'])) > math.ceil(self.__current_comment.length() * 1.35)

    def __introductory_comment(self, entity):
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

    def __next_comment(self):
        self.__comment_index += 1
        if self.__comment_index < len(self.__comments):
            self.__current_comment = self.__comments[self.__comment_index]
    
    def __determine_category(self, type):
        return PYTHON_LABELS[type]

    def __is_copyright_comment(self, comment_text):
        copyright_comment = False
        for keyword in COPYRIGHT_IDENTIFIERS:
            copyright_comment = copyright_comment or keyword in comment_text or keyword.capitalize()in comment_text
        return copyright_comment
    
    def __is_task_comment(self, comment_text):
        task_comment = False
        for keyword in TASK_IDENTIFIERS:
            task_comment = task_comment or keyword in comment_text
        return task_comment
