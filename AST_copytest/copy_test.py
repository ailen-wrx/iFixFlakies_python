"Usage: python3 copy_test.py cleaner_fullpath victim_fullpath combination_path"

import ast
import sys
from unparse import Unparser
from io import StringIO


class get_origin_astInfo(ast.NodeVisitor):
    def __init__(self,node):
        self.import_num = 0
        self.body = node.body

    def get_import_num(self):
        for object in self.body:
            if type(object) == ast.Import or type(object) == ast.ImportFrom:
                self.import_num += 1
        return self.import_num


def fix_victim(cleaner_fullpath, victim_fullpath, combination_path):

    victim_path=victim_fullpath.split('::')[0]
    victim_testfunc=victim_fullpath.split('::')[1]

    cleaner_path=cleaner_fullpath.split('::')[0]
    cleaner_testfunc = cleaner_fullpath.split('::')[1]

    with open(victim_path, "r") as victim:
        tree_victim = ast.parse(victim.read())
        #victim_info = get_origin_astInfo(tree_victim)
        #victim_import_num = victim_info.get_import_num()

    with open(cleaner_path, "r") as cleaner:
        tree_cleaner = ast.parse(cleaner.read())
        cleaner_info = get_origin_astInfo(tree_cleaner)
        cleaner_import_num = cleaner_info.get_import_num()

    # copy Import and ImportFrom modules
    tree_victim.body.insert(0, tree_cleaner.body[0:cleaner_import_num])

    # copy test body
    for cleaner_obj in [func for func in ast.walk(tree_cleaner) if isinstance(func, ast.FunctionDef)]:
        if cleaner_obj.name == cleaner_testfunc:
            insert_node=cleaner_obj.body
            break
    for victim_obj in [func for func in ast.walk(tree_victim) if isinstance(func, ast.FunctionDef)]:
        if victim_obj.name == victim_testfunc:
            victim_obj.body.insert(0,insert_node)
            break
    
    ast.fix_missing_locations(tree_victim)
    buf = StringIO()
    Unparser(tree_victim, buf)
    buf.seek(0)
    #print(buf.read())
    with open(combination_path, "w") as combination:
        combination.write(buf.read())

if __name__ == "__main__":
    
    cleaner_fullpath, victim_fullpath, combination_path = sys.argv[1:4]
    fix_victim(cleaner_fullpath, victim_fullpath, combination_path)
