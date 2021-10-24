
"Usage: python3 copy_test.py polluter_fullpath cleaner_fullpath victim_fullpath combination_path"

import ast
import re
import os
import sys
from unparse import Unparser
from io import StringIO
import hashlib, binascii


class get_origin_astInfo(ast.NodeVisitor):
    def __init__(self,node):
        self.import_num = 0
        self.body = node.body

    def get_import_num(self):
        for object in self.body:
            if type(object) == ast.Import or type(object) == ast.ImportFrom:
                self.import_num += 1
        return self.import_num


def fix_victim(polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path):

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

    # copy unique Import and ImportFrom modules
    for import_obj in [module for module in ast.walk(tree_cleaner) if isinstance(module,ast.Import) or isinstance(module,ast.ImportFrom)]:
        if ast.dump(import_obj) not in [ast.dump(module) for module in ast.walk(tree_victim) if isinstance(module,ast.Import) or isinstance(module,ast.ImportFrom)]:
            print(ast.dump(import_obj))
            tree_victim.body.insert(0,import_obj)

            
    # get helper code from cleaner, handle setup, body and teardown 'module, method, class, function'
    # setup_module,setup_class,setup_function,setup_method,test_body,teardown_method,teardown_function,teardown_class,teardown_module

    name_node_dict={'setup_module' : None, 'setup_class' : None, 'setup_function' : None, 'setup_method' : None, cleaner_testfunc : None,
                    'teardown_method' : None, 'teardown_function' : None, 'teardown_class' : None, 'teardown_module' : None}
    
    for eachfunc in [func for func in ast.walk(tree_cleaner) if isinstance(func, ast.FunctionDef)]:
        if eachfunc.name in name_node_dict:
            name_node_dict[eachfunc.name]=eachfunc.body
    print(name_node_dict)
    
    insert_nodes_keys = [key for key in name_node_dict if name_node_dict[key] != None] 
    pre_node_key = insert_nodes_keys[0]
    pre_node = name_node_dict[pre_node_key]
    
    if len(insert_nodes_keys)>1:
        for key in len(insert_nodes_keys)[1:]:
            print(key, name_node_dict[key])
            pre_node = name_node_dict[key].insert(0, pre_node)
    insert_node=pre_node       

    
    # get victim test body 
    for victim_obj in [func for func in ast.walk(tree_victim) if isinstance(func, ast.FunctionDef)]:
        if victim_obj.name == victim_testfunc:
            victim_node=victim_obj.body
            break


        
    md5_path=setup_dir(polluter_fullpath, cleaner_fullpath, victim_fullpath)
    
    origin_insert_node=insert_node

    while True:
        print('***********')
        victim_node.insert(0,insert_node) 
        ast.fix_missing_locations(tree_victim)
        buf = StringIO()
        Unparser(tree_victim, buf)
        buf.seek(0)
        #print(buf.read())
        with open(combination_path, "w") as combination:
            combination.write(buf.read())
        if (run_tests(md5_path,polluter_fullpath,combination_path+'::'+victim_testfunc)) !='passed':
            break
        #else:
          # minimize code 
            

def setup_dir(polluter_fullpath, cleaner_fullpath, victim_fullpath):
    md5=hashlib.md5()
    md5.update(polluter_fullpath.encode())
    md5.update(cleaner_fullpath.encode())
    md5.update(victim_fullpath.encode())
    md5_Digest = md5.hexdigest()
    
    os.system('rm -rf '+md5_Digest)
    os.system('mkdir '+ md5_Digest)
    print('done')
    return md5_Digest
    
        
def run_tests(dir_md5, polluter_fullpath, victim_fullpath):
    run_cmd="python3 -m pytest "+polluter_fullpath+' '+victim_fullpath +' --csv '+dir_md5+'/'+dir_md5+'_result.csv' 
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(run_cmd)
    os.system(run_cmd)
    print(victim_fullpath)
    victim_result='grep -n '+victim_fullpath + ' ' + dir_md5+'/'+dir_md5+'_result.csv' + ' | cut -d\',\' -f7 '
    print(victim_result)
    #os.system(victim_result)
    result = os.popen(victim_result)  
    res = result.read()
    return res  
    

if __name__ == "__main__":
    
    polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path = sys.argv[1:5]
    fix_victim(polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path)
    
