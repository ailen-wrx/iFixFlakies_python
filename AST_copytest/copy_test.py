"Usage: python3 copy_test.py cleaner_path victim_path combination_path"

import ast
import sys
from unparse import Unparser
from io import StringIO


class get_origin_astInfo(ast.NodeVisitor):
    def __init__(self,node):
        self.import_num=0
        self.body=node.body

    def get_import_num(self):
        for object in self.body:
            if type(object)==(ast.Import or ast.ImportFrom):
                self.import_num+=1
        return self.import_num


def fix_victim(cleaner_path,victim_path,combination_path):

    with open(victim_path, "r") as victim:
        tree_victim = ast.parse(victim.read())
        victim_info=get_origin_astInfo(tree_victim)
        victim_import_num=victim_info.get_import_num()

    with open(cleaner_path, "r") as cleaner:
        tree_cleaner = ast.parse(cleaner.read())
        cleaner_info=get_origin_astInfo(tree_cleaner)
        cleaner_import_num=cleaner_info.get_import_num()

    # copy Import and ImportFrom modules
    tree_victim.body.insert(0,tree_cleaner.body[0:cleaner_import_num])

    # copy classDef modules in 2 cases(if __name__ == "__main__")
    if type(tree_cleaner.body[-1])==(ast.If): 
        tree_victim.body.insert(cleaner_import_num+victim_import_num,tree_cleaner.body[cleaner_import_num:-1])
    else:
        tree_victim.body.insert(cleaner_import_num+victim_import_num,tree_cleaner.body[cleaner_import_num:])

    ast.fix_missing_locations(tree_victim)
    buf = StringIO()
    Unparser(tree_victim, buf)
    buf.seek(0)
    #print(buf.read())
    with open(combination_path, "w") as combination:
        combination.write(buf.read())

if __name__ == "__main__":
    
    cleaner_path,victim_path,combination_path = sys.argv[1:4]
    fix_victim(cleaner_path,victim_path,combination_path)
    
