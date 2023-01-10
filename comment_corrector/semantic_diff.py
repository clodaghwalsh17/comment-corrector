import subprocess
import sys

SEMANTIC_DIFF_TOOL_PATH = "target/semanticDiff-1-jar-with-dependencies.jar"

def diff(files, language):
    try:
        return run_gumtree(files, language)
    except Exception as e:
        print(e)  
        sys.exit()

def run_gumtree(files, language):  
    process = subprocess.run(["java", "-jar", SEMANTIC_DIFF_TOOL_PATH, language, files[0], files[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if not process.stderr:
        return process.stdout
    else:
        raise Exception("An error occurred during semantic differencing. A Java program using the GumTree API performs semantic differencing. \n{}".format(process.stderr))