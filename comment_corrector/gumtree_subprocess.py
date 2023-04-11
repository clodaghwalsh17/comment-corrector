import subprocess
import sys
import json

SEMANTIC_DIFF_TOOL_PATH = "target/semanticDiff-1-jar-with-dependencies.jar"

# Return a dictionary with the keys type, pos, length, children  
# The value for type, pos, length is a string
# The value for children is a list of dictionaries with the keys mentioned above, this means the tree returned is a recursive data structure
def source_to_tree(file):
    try:
        tree = json.loads(gumtree_jsontree(file))
        return tree['root']
    except Exception as e:
        print(e)  
        sys.exit(1)

def gumtree_editscript(files):  
    process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, "editscript", files[0], files[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if not process.stderr:
        return process.stdout
    else:
        raise Exception("An error occurred during analysis. A Java program using the GumTree API generates the edit script between the two versions of the file. Java program error: {}".format(process.stderr))
    
def gumtree_jsontree(file):
    process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, "jsontree", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if not process.stderr:
        return process.stdout
    else:
        raise Exception("An error occurred during analysis. A Java program using the GumTree API produces a tree like representation of the source code in JSON format. Java program error: {}".format(process.stderr))