
"Usage: python3 copy_test.py cleaner_fullpath victim_fullpath combination_path"

import ast
import csv
import re
import os
import sys
import time
from unparse import Unparser
from io import StringIO
import hashlib, binascii
#result_path='/home/yyy/patch_result3.csv'


class get_origin_astInfo(ast.NodeVisitor):
    def __init__(self,node):
        self.import_num = 0
        self.body = node.body

    def get_import_num(self):
        for object in self.body:
            if type(object) == ast.Import or type(object) == ast.ImportFrom:
                self.import_num += 1
        return self.import_num


def fix_victim(project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path,result_path):

    patch_list=[]
    
    victim_path=victim_fullpath.split('::')[0]
    victim_testfunc=victim_fullpath.split('::')[-1]

    cleaner_path=cleaner_fullpath.split('::')[0]
    cleaner_testfunc = cleaner_fullpath.split('::')[-1]

    with open(victim_path, "r") as victim:
        tree_victim = ast.parse(victim.read())
        #victim_info = get_origin_astInfo(tree_victim)
        #victim_import_num = victim_info.get_import_num()

    print(cleaner_path,cleaner_testfunc)
    with open(cleaner_path, "r") as cleaner:
        tree_cleaner = ast.parse(cleaner.read())
        cleaner_info = get_origin_astInfo(tree_cleaner)
        cleaner_import_num = cleaner_info.get_import_num()

    md5_path = setup_dir(polluter_fullpath, cleaner_fullpath, victim_fullpath)
    pcv_result=run_tests_pcv(md5_path, polluter_fullpath, cleaner_fullpath, victim_fullpath)
    pv_result=run_tests_pv(md5_path,polluter_fullpath,victim_fullpath)
    if pv_result.strip()!='failed':
        pv_10_times_result=[]
        for i in range(0,10):
            tmp_result=run_tests_pv(md5_path,polluter_fullpath,victim_fullpath)
            pv_10_times_result.append(tmp_result)
        if 'failed' in pv_10_times_result:
            pv_result='ND'

    patch_time_1st = None
    patch_time_all = None
    can_copy_work=None            
    if pv_result.strip() == 'failed':
        # copy unique Import and ImportFrom modules
        for import_obj in [module for module in ast.walk(tree_cleaner) if
                           isinstance(module, ast.Import) or isinstance(module, ast.ImportFrom)]:
            if ast.dump(import_obj) not in [ast.dump(module) for module in ast.walk(tree_victim) if
                                            isinstance(module, ast.Import) or isinstance(module, ast.ImportFrom)]:
                tree_victim.body.insert(0, import_obj)

        # get helper code from cleaner, handle setup, body and teardown 'module, method, class, function'
        # setup_module,setup_class,setup_function,setup_method,test_body,teardown_method,teardown_function,teardown_class,teardown_module

        name_node_dict = {'setup_module': None, 'setup_class': None, 'setup_function': None, 'setup_method': None,
                          cleaner_testfunc: None,
                          'teardown_method': None, 'teardown_function': None, 'teardown_class': None,
                          'teardown_module': None}

        for eachfunc in [func for func in ast.walk(tree_cleaner) if isinstance(func, ast.FunctionDef)]:
            if eachfunc.name in name_node_dict:
                name_node_dict[eachfunc.name] = eachfunc.body

        insert_nodes_keys = [key for key in name_node_dict if name_node_dict[key] != None]

        pre_node_key = insert_nodes_keys[0]
        pre_node = name_node_dict[pre_node_key]

        if len(insert_nodes_keys) > 1:
            for key in len(insert_nodes_keys)[1:]:
                pre_node = name_node_dict[key].insert(0, pre_node)
        insert_node = pre_node

        # get victim test body
        for victim_obj in [func for func in ast.walk(tree_victim) if isinstance(func, ast.FunctionDef)]:
            if victim_obj.name == victim_testfunc:
                victim_node = victim_obj.body
                break

    

        origin_insert_node = insert_node
        origin_tree_victim = tree_victim
        origin_victim_node = victim_node

        print('******************************************')

        tmp_origin_victim = origin_victim_node
        tmp_tree_victim = origin_tree_victim
        tmp_insert_node = insert_node

        tmp_origin_victim.insert(0, tmp_insert_node)
        ast.fix_missing_locations(tmp_tree_victim)

        insert_buf = StringIO()
        Unparser(tmp_insert_node, insert_buf)
        insert_buf.seek(0)
        insert_content = insert_buf.read()
        insert_statement_list = insert_content.split('\n')
        while '' in insert_statement_list:
            insert_statement_list.remove('')

        buf = StringIO()
        Unparser(tmp_tree_victim, buf)
        buf.seek(0)
        edited_content = buf.read()

        with open(combination_path, "w") as combination:
            combination.write(edited_content)
        result = (run_tests_pv(md5_path, polluter_fullpath,
                               combination_path + '::' + '::'.join(victim_fullpath.split('::')[1:])))

        tmp_origin_victim.remove(tmp_insert_node)

        can_copy_work = False
        if result.strip() == 'passed':
            can_copy_work = True

        # minimize code by delta debugging
        n = 2
        start_time = time.perf_counter()
        patch_num = 0
        patch_time_1st = None
        patch_time_all = None
        while len(insert_statement_list) >= 2:
            start = 0
            print('******************************************************')
            subset_length = len(insert_statement_list) // n
            pollution_is_cleaned = False
            while start < len(insert_statement_list):
                this_round_insert_list = insert_statement_list[:start] + insert_statement_list[start + subset_length:]
                this_round_insert_code = '\n'.join(this_round_insert_list)

                tmp_tree_victim = origin_tree_victim
                tmp_origin_victim = origin_victim_node
                tmp_insert_node = ast.parse(this_round_insert_code)

                tmp_origin_victim.insert(0, tmp_insert_node)
                ast.fix_missing_locations(tmp_tree_victim)

                tmp_buf = StringIO()
                Unparser(tmp_insert_node, tmp_buf)
                tmp_buf.seek(0)
                tmp_content = tmp_buf.read()

                # print('@@@@@@@@@@@@@@@@@@@@')
                # print(tmp_content)

                buf = StringIO()
                Unparser(tmp_tree_victim, buf)
                buf.seek(0)
                edited_content = buf.read()

                combination_path = combination_path.replace('com', 'com2')
                with open(combination_path, "w") as combination:
                    combination.write(edited_content)

                tmp_origin_victim.remove(tmp_insert_node)

                if (run_tests_pv(md5_path, polluter_fullpath, combination_path + '::' + '::'.join(
                        victim_fullpath.split('::')[1:]))).strip() == 'passed':
                    patch_time = time.perf_counter()
                    patch_num += 1
                    if patch_num == 1:
                        patch_time_1st = patch_time - start_time
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CAN BE A PATCH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n',
                          tmp_content)
                    patch_list.append(tmp_content)
                    insert_statement_list = this_round_insert_list
                    n = max(n - 1, 2)
                    pollution_is_cleaned = True
                    break
                start = start + subset_length
            if not pollution_is_cleaned:
                n = min(n * 2, len(insert_statement_list))
                if n == len(insert_statement_list):
                    break
        end_time = time.perf_counter()
        patch_time_all = end_time - start_time

    
    with open(result_path,'a+') as f:
        csv_write = csv.writer(f)
        result=[project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5_path,pv_result,pcv_result,can_copy_work,patch_time_1st,patch_time_all]

        for each in patch_list:
            result.append(each)
        
        csv_write.writerow(result)
       
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
    
        
def run_tests_pv(dir_md5, polluter_fullpath, victim_fullpath):
    run_cmd_pv="python3 -m pytest "+polluter_fullpath+' '+victim_fullpath +' --csv '+dir_md5+'/'+dir_md5+'_pv_result.csv' 
    os.system(run_cmd_pv)
   
    get_pv_result='grep -n '+victim_fullpath +' '+ dir_md5+'/'+dir_md5+'_pv_result.csv' + ' | cut -d\',\' -f7 '
   
    pv_result = os.popen(get_pv_result)  
    pv_res = pv_result.read()
    save_cmd="echo "+polluter_fullpath + ',' +victim_fullpath+','+dir_md5+','+pv_res.strip()+ " >> /home/yyy/testresultcom.csv"
   
    os.system(save_cmd)
    return pv_res  

def run_tests_pcv(dir_md5, polluter_fullpath, cleaner_fullpath, victim_fullpath):
    run_cmd_pcv="python3 -m pytest "+polluter_fullpath+' '+cleaner_fullpath+' '+victim_fullpath +' --csv '+dir_md5+'/'+dir_md5+'_pcv_result.csv'
    os.system(run_cmd_pcv)

    get_pcv_result='grep -n '+victim_fullpath +' '+ dir_md5+'/'+dir_md5+'_pcv_result.csv' + ' | cut -d\',\' -f7 '
    pcv_result=os.popen(get_pcv_result)
    pcv_res=pcv_result.read()
    save_cmd="echo "+polluter_fullpath + ',' +cleaner_fullpath+','+victim_fullpath+','+dir_md5+','+pcv_res.strip()+ " >> /home/yyy/testresultcom.csv"

    os.system(save_cmd)
    return pcv_res


if __name__ == "__main__":
    
    project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path, result_path = sys.argv[1:8]
    fix_victim(project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path,result_path)
    
