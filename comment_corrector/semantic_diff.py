from comment_corrector.edit_script_action import EditScriptAction
from comment_corrector.utils import Utils
from comment_corrector.gumtree_subprocess import *
import sys
import re

class SemanticDiff:

    def __init__(self, files):
        self.__files = files
        self.__edit_script_actions = []
        self.__refactored_names = {}
        self.__unreferenced_names = []
        self.__deleted_names = []
        self.__diff()
    
    def edit_script_actions(self):
        return self.__edit_script_actions
    
    def refactored_names(self):
        return self.__refactored_names
    
    def deleted_names(self):
        return self.__deleted_names

    def unreferenced_names(self):
        return self.__unreferenced_names
    
    def __diff(self):
        try:
            edit_script = gumtree_editscript(self.__files)
            self.__process_edit_script(edit_script)
        except Exception as e:
            print(e)  
            sys.exit(1)

    def __process_edit_script(self, edit_script):
        '''
        The edit script produced by GumTree follows the following format:
        
        ===
        insert-node
        ---
        import_from [6,24]
        to
        simple_stmt [0,6]
        at 0
        ===
        update-node
        ---
        name: x [0,1]
        replace x by math
        ===
        move-tree
        ---
        name: x [0,1]
        to
        import_from [6,24]
        at 0
        ===
        update-node
        ---
        operator: = [2,3]
        replace = by *
        ===
        move-tree
        ---
        operator: = [2,3]
        to
        import_from [6,24]
        at 1
        ===
        delete-node
        ---
        number: 0 [4,5]
        ===
        delete-node
        ---
        expr_stmt [0,5]

        Comment Corrector only relies on the action type, file position and possible destination.
        The action type can be one of insert-node, update-node, delete-node, insert-tree, move-tree, delete-tree
        '''
        actions = edit_script.split("===\n")

        for action in actions[1:]:
            if action == '':
                continue
            
            action_type = action[:action.index('\n')]
            file_positions = re.search("\[*([0-9,]+)\]", action).group(1).split(",")
            affects_param = Utils.match_phrase("param")(action) is not None 
            affects_return = re.search('return', action, re.IGNORECASE) is not None 

            # Shorten edit script produced by removing action types that provide little information
            if action_type == "insert-tree" and not affects_param and not self.__relevant_insert_tree(action):
                continue                 
            
            replace_index = action.find('replace')
            if replace_index != -1:
                replace_info = action[replace_index:].strip()
                # An update-node provides information on the previous and current value
                # This is present in the edit script following the format "replace x by y"
                initial_name = replace_info.split(" ")[1]
                if self.__is_valid_name(initial_name):
                    updated_name = replace_info.split(" ")[3]
                    self.__refactored_names[initial_name] = updated_name         
                    self.__extract_unreferenced_names(initial_name)                    

            if action_type == "delete-tree":
                name_index = action.find('name')
                if name_index != -1:
                    name = action[name_index:].removeprefix("name: ").split(" ")[0]
                    self.__deleted_names.append(name)
                    self.__extract_unreferenced_names(name)            

            to_index = action.find('to\n')
            if to_index != -1:
                dst_start = int(re.search("\[*([0-9,]+)\]", action[to_index:]).group(1).split(",")[0])
                dst_end = int(re.search("\[*([0-9,]+)\]", action[to_index:]).group(1).split(",")[1])
                self.__edit_script_actions.append(EditScriptAction(action_type, int(file_positions[0]), int(file_positions[1]), dst_start=dst_start, dst_end=dst_end, affects_function=affects_param or affects_return))
            else:
                self.__edit_script_actions.append(EditScriptAction(action_type, int(file_positions[0]), int(file_positions[1]), affects_function=affects_param or affects_return))    

    def __is_valid_name(self, text):
        return re.search("[a-zA-Z]", text) is not None

    def __extract_unreferenced_names(self, name):
        if "_" in name:
            self.__unreferenced_names.append(' '.join(name.split("_")))
        if "-" in name:
            self.__unreferenced_names.append(' '.join(name.split("-")))
        if re.search(r'[A-Z]', name) is not None:
            self.__unreferenced_names.append(' '.join(re.split('[A-Z]', name)))     
    
    def __relevant_insert_tree(self, insert_tree):
        return re.search(r'to \b(suite|while_stmt)\b .* at 0', re.sub(r"\n", " ", insert_tree)) is not None or re.search('if_stmt', insert_tree) is not None  