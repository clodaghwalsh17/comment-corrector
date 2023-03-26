from comment_corrector.utils import Utils
import os
 
GITHUB_WORKSPACE = '/github/workspace/'

for (dirpath, _, filenames) in os.walk(GITHUB_WORKSPACE):
    for filename in filenames: 
        if Utils.get_file_extension(filename) == ".py":
            print(os.path.join(dirpath, filename))