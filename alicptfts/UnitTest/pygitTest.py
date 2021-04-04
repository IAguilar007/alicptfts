
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import *
#import os os.environ["GIT_PYTHON_REFRESH"] = "quiet" import git
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURRENT_DIR)
repo = Repo(u'alicptfts')
#print(self.rorepo.working_tree_dir)
#repo = Repo(CURRENT_DIR)

