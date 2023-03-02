from comment_corrector.edit_script_action import EditScriptAction
import subprocess
import sys
import re

SEMANTIC_DIFF_TOOL_PATH = "target/semanticDiff-1-jar-with-dependencies.jar"

def diff(files):
    try:
        edit_script = __gumtree_editscript(files)
        return __convert_to_actions_list(edit_script)
    except Exception as e:
        print(e)  
        sys.exit()

def __gumtree_editscript(files):  
    process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, "editscript", files[0], files[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if not process.stderr:
        return process.stdout
    else:
        raise Exception("An error occurred during analysis. A Java program using the GumTree API generates the edit script between the two versions of the file. Java program error: {}".format(process.stderr))

def __convert_to_actions_list(edit_script):
    actions = edit_script.split("===\n")
    edit_script_actions = []

    for action in actions[1:]:
        if action == '':
            continue
        type = action[:action.index('\n')]
        file_positions = re.search("\[*([0-9,]+)\]", action).group(1).split(",")
        index = action.find('to\n')
        
        if index == -1:
            destination = None
        else:
            destination = action[index+3:].split(" ")[0]    

        edit_script_actions.append(EditScriptAction(type, int(file_positions[0]), int(file_positions[1]), destination))

    return edit_script_actions

def source_to_tree(file):
    try:
        return __gumtree_jsontree(file)
    except Exception as e:
        print(e)  
        sys.exit()

def __gumtree_jsontree(file):
    process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, "jsontree", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if not process.stderr:
        return process.stdout
    else:
        raise Exception("An error occurred during analysis. A Java program using the GumTree API produces a tree like representation of the source code in JSON format. Java program error: {}".format(process.stderr))