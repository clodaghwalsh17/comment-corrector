import subprocess
import sys

SEMANTIC_DIFF_TOOL_PATH = "target/semanticDiff-1-jar-with-dependencies.jar"

def diff(files):
    try:
        return __gumtree_editscript(files)
    except Exception as e:
        print(e)  
        sys.exit()

def __gumtree_editscript(files):  
    process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, "editscript", files[0], files[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if not process.stderr:
        return process.stdout
    else:
        raise Exception("An error occurred during analysis. A Java program using the GumTree API generates the edit script between the two versions of the file. Java program error: {}".format(process.stderr))

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