from comment_corrector.edit_script_action import EditScriptAction
import subprocess
import sys
import re
import json

SEMANTIC_DIFF_TOOL_PATH = "target/semanticDiff-1-jar-with-dependencies.jar"

class SemanticDiff:

    def __init__(self, files):
        self.__file1 = files[0]
        self.__file2 = files[1]
        self.__edit_script_actions = []
        self.__refactored_names = {}
        self.__refactored_name_components = []
        self.__diff()
    
    def source_to_tree(self):
        return self.__convert_source_to_tree(self.__file1)
    
    def edit_script_actions(self):
        return self.__edit_script_actions
    
    def refactored_names(self):
        return self.__refactored_names, self.__refactored_name_components
    
    def __convert_source_to_tree(self, file):
        try:
            tree = json.loads(self.__gumtree_jsontree(file))
            return tree['root']

        except Exception as e:
            print(e)  
            sys.exit()

    def __diff(self):
        try:
            edit_script = self.__gumtree_editscript()
            self.__process_edit_script(edit_script)
        except Exception as e:
            print(e)  
            sys.exit()

    def __gumtree_editscript(self):  
        process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, "editscript", self.__file1, self.__file2], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if not process.stderr:
            return process.stdout
        else:
            raise Exception("An error occurred during analysis. A Java program using the GumTree API generates the edit script between the two versions of the file. Java program error: {}".format(process.stderr))

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
            
            type = action[:action.index('\n')]
            # Shorten edit script produced by removing action types that provide little information
            if type == "delete-node" or type == "insert-tree":
                continue

            file_positions = re.search("\[*([0-9,]+)\]", action).group(1).split(",")
            
            replace_index = action.find('replace')
            if replace_index != -1:
                replace_info = action[replace_index:].strip()
                # An update-node provides information on the previous and current value
                # This is present in the edit script following the format "replace x by y"
                initial_name = replace_info.split(" ")[1]
                if self.__is_valid_name(initial_name):
                    updated_name = replace_info.split(" ")[3]
                    self.__refactored_names[initial_name] = updated_name         

                    if "_" in initial_name:
                        self.__refactored_name_components.append(' '.join(initial_name.split("_")))
                    if "-" in initial_name:
                        self.__refactored_name_components.append(' '.join(initial_name.split("-")))
                    if re.search(r'[A-Z]', initial_name) is not None:
                        self.__refactored_name_components.append(' '.join(re.split('[A-Z]', initial_name)))                   

            to_index = action.find('to\n')
            if to_index != -1:
                dst_start = int(re.search("\[*([0-9,]+)\]", action[to_index:]).group(1).split(",")[0])
                dst_end = int(re.search("\[*([0-9,]+)\]", action[to_index:]).group(1).split(",")[1])
                self.__edit_script_actions.append(EditScriptAction(type, int(file_positions[0]), int(file_positions[1]), dst_start=dst_start, dst_end=dst_end))
            else:
                self.__edit_script_actions.append(EditScriptAction(type, int(file_positions[0]), int(file_positions[1])))    

    def __gumtree_jsontree(self, file):
        process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, "jsontree", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if not process.stderr:
            return process.stdout
        else:
            raise Exception("An error occurred during analysis. A Java program using the GumTree API produces a tree like representation of the source code in JSON format. Java program error: {}".format(process.stderr))
        
    def __is_valid_name(self, text):
        return re.search("[a-zA-Z]", text) is not None