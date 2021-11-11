
"Usage: python3 copy_test.py cleaner_fullpath victim_fullpath combination_path"

import ast
import csv
import difflib
from py import io
import re
import os
import shutil
import sys
import time
import pytest
import pandas as pd
from unparse import Unparser
from io import StringIO
import hashlib, binascii

CACHE_DIR='../patchercache/'


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

    cache_in_tests=[]
    patch_list=[]

    victim_path=victim_fullpath.split('::')[0]
    victim_testfunc=victim_fullpath.split('::')[-1]
    if '[' in victim_testfunc and ']' in victim_testfunc:
        start=victim_testfunc.index('[')
        end=victim_testfunc.index(']')+1
        par=victim_testfunc[start:end]
        print(par)
        final=victim_testfunc.replace(str(par),"")
        #print(final)
        victim_testfunc=final
    victim_class=None
    if len(victim_fullpath.split('::'))>2:
        victim_class=victim_fullpath.split('::')[-2]

    cleaner_path=cleaner_fullpath.split('::')[0]
    cleaner_testfunc = cleaner_fullpath.split('::')[-1]
    if '[' in cleaner_testfunc and ']' in cleaner_testfunc:
        start=cleaner_testfunc.index('[')
        end=cleaner_testfunc.index(']')+1
        par=cleaner_testfunc[start:end]
        print(par)
        final=cleaner_testfunc.replace(str(par),"")
        #print(final)
        cleaner_testfunc=final

    cleaner_class=None
    if len(cleaner_fullpath.split('::'))>2:
        cleaner_class=cleaner_fullpath.split('::')[-2]

    
    with open(victim_path, "r") as victim:
        tree_victim = ast.parse(victim.read())
       
    print(cleaner_path,cleaner_testfunc)
    with open(cleaner_path, "r") as cleaner:
        tree_cleaner = ast.parse(cleaner.read())
        cleaner_info = get_origin_astInfo(tree_cleaner)
        cleaner_import_num = cleaner_info.get_import_num()

        
    md5 = get_md5(polluter_fullpath, cleaner_fullpath, victim_fullpath)


    try:
        pcv_result=run_tests_pcv(project, md5, polluter_fullpath, cleaner_fullpath, victim_fullpath)
        pv_result=run_tests_pv(project, md5,polluter_fullpath,victim_fullpath)

    except:
        with open(result_path,'a+') as f:
            csv_write = csv.writer(f)
            result=[project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5,'PCV_ERROR']
            csv_write.writerow(result)
            exit(1)
            
    minimal_patch_file=None
    patch_time_1st = None
    patch_time_all = None
    can_copy_work = None
    
    if pv_result.strip() == 'failed' and pcv_result.strip() =='passed':
        # copy unique Import and ImportFrom modules
        
        for import_obj in [module for module in ast.walk(tree_cleaner) if
                           isinstance(module, ast.Import) or isinstance(module, ast.ImportFrom)]:
            if ast.dump(import_obj) not in [ast.dump(module) for module in ast.walk(tree_victim) if
                                            isinstance(module, ast.Import) or isinstance(module, ast.ImportFrom)]:
                tree_victim.body.insert(0, import_obj)
     
        # get helper code from cleaner, handle setup, body and teardown 'module, method, class, function'
        # setup_module,setup_class,setup_function,setup_method,test_body,teardown_method,teardown_function,teardown_class,teardown_module

        name_node_dict = {'setup_module': None, 'setUpClass': None, 'setup_function': None, 'setup_method': None,
                          cleaner_testfunc: None,
                          'teardown_method': None, 'teardown_function': None, 'tearDownClass': None,
                          'teardown_module': None}

        if cleaner_class:
           for clean_class in [node for node in ast.walk(tree_cleaner) if isinstance(node, ast.ClassDef)]:
               if clean_class.name == cleaner_class:
                   for clean_obj in [func for func in ast.iter_child_nodes(clean_class) if isinstance(func, ast.FunctionDef)]:
                     
                        if clean_obj.name in name_node_dict:
                            name_node_dict[clean_obj.name] = clean_obj.body
                   break


           insert_nodes_keys = [key for key in name_node_dict if name_node_dict[key] != None]
           pre_node_key = insert_nodes_keys[0]
           pre_node = name_node_dict[pre_node_key]

           if len(insert_nodes_keys) > 1:
               for key in insert_nodes_keys[1:]:
                   name_node_dict[key].insert(0, pre_node)
                   pre_node = name_node_dict[key]
           insert_node = pre_node

        else:
            for eachfunc in [func for func in ast.walk(tree_cleaner) if isinstance(func, ast.FunctionDef)]:
                if eachfunc.name in name_node_dict:
                    name_node_dict[eachfunc.name] = eachfunc.body

            insert_nodes_keys = [key for key in name_node_dict if name_node_dict[key] != None]

            pre_node_key = insert_nodes_keys[0]
            pre_node = name_node_dict[pre_node_key]

            if len(insert_nodes_keys) > 1:
                 for key in insert_nodes_keys[1:]:
                    pre_node = name_node_dict[key].insert(0, pre_node)
            insert_node = pre_node

         
            
        # get victim test body
        if victim_class:
            for vic_class in [node for node in ast.walk(tree_victim) if isinstance(node,ast.ClassDef)]:
                if vic_class.name == victim_class:
                    for victim_obj in [func for func in ast.iter_child_nodes(vic_class) if isinstance(func,ast.FunctionDef)]:
                        print(victim_obj)             
                        if victim_obj.name == victim_testfunc:
                               victim_node = victim_obj.body
                               break

        else:
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

    #    for each in [func for func in ast.walk(tree_victim) if isinstance(func, ast.expr)]:
     #       print(each.lineno)
        print(ast.expr,'++++++++++++++++++++++++++++++++')
        tmp_origin_victim.insert(0, tmp_insert_node)
        ast.fix_missing_locations(tmp_tree_victim)

        insert_buf = StringIO()

        Unparser(tmp_insert_node, insert_buf)
        insert_buf.seek(0)
        insert_content = insert_buf.read()
        insert_statement_list = insert_content.split('\n')
        print(insert_statement_list)
        while '' in insert_statement_list:
            insert_statement_list.remove('')

        try:
            buf = StringIO()
            Unparser(tmp_tree_victim, buf)
            buf.seek(0)
            edited_content = buf.read()
        except IndentationError:
            can_copy_work=False

        with open(combination_path, "w") as combination:
            combination.write(edited_content)
        result = (run_tests_pv(project, md5, polluter_fullpath,
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
        roundnum=0
        minimal_patch_file= None
        while len(insert_statement_list) >= 2:
            start = 0
            subset_length = len(insert_statement_list) // n
            pollution_is_cleaned = False
            while start < len(insert_statement_list):
                this_round_insert_list = insert_statement_list[:start] + insert_statement_list[start + subset_length:]
                this_round_insert_code = '\n'.join(this_round_insert_list)

                tmp_tree_victim = origin_tree_victim
                tmp_origin_victim = origin_victim_node


                try:

                    tmp_insert_node = ast.parse(this_round_insert_code)


                    tmp_origin_victim.insert(0, tmp_insert_node)
                    print('&&&&&&&&&&&&&_',tmp_insert_node.lineno)

                    ast.fix_missing_locations(tmp_tree_victim)
                    can_be_inserted=True
                except:# IndentationError:
                    can_be_inserted=False
                tmp_buf = StringIO()
                Unparser(tmp_insert_node, tmp_buf)
                tmp_buf.seek(0)
                tmp_content = tmp_buf.read()

                # print('@@@@@@@@@@@@@@@@@@@@')
                # print(tmp_content)

                #if can_be_inserted:
                buf = StringIO()
                Unparser(tmp_tree_victim, buf)
                buf.seek(0)
                edited_content = buf.read()

                combination_path = combination_path.replace('patch', 'patch'+str(roundnum))
                roundnum+=1
                with open(combination_path, "w") as combination:
                    combination.write(edited_content)

                if can_be_inserted:
                    tmp_origin_victim.remove(tmp_insert_node)
                can_patch_work=(run_tests_pv(project,md5, polluter_fullpath, combination_path + '::' + '::'.join(victim_fullpath.split('::')[1:])))
               # shutil.copyfile(combination_path, CACHE_DIR+combination_path)
                cache_in_tests.append(combination_path)

                if can_patch_work.strip() == 'passed':
                    patch_time = time.perf_counter()
                    patch_num += 1
                    if patch_num == 1:
                        patch_time_1st = patch_time - start_time
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CAN BE A PATCH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n',
                          tmp_content)
                    minimal_patch_file=combination_path
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
        if patch_time_1st:
            patch_time_all = end_time - start_time


#    if minimal_patch_file:
#        print(victim_path,minimal_patch_file)
#        generate_diff(victim_path,minimal_patch_file)
        

    with open(result_path,'a+') as f:
        csv_write = csv.writer(f)
        result=[project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5,pv_result,pcv_result,can_copy_work,patch_time_1st,patch_time_all]

        for each in patch_list:
            result.append(each)
        
        csv_write.writerow(result)
    for each in cache_in_tests:
        if each != minimal_patch_file:
            os.remove(each)

def generate_diff(original_victim,fixed_victim):

    original_victim_file=open(original_victim,'r')
    fixed_victim_file=open(fixed_victim,'r')
    diff=difflib.ndiff(original_victim_file.readlines(),fixed_victim_file.readlines())
    delta= ''.join(x[2:] for x in diff if x.startswith('- '))
    print(delta)


    
def get_md5(polluter_fullpath, cleaner_fullpath, victim_fullpath):
    md5=hashlib.md5()
    md5.update(polluter_fullpath.encode())
    md5.update(cleaner_fullpath.encode())
    md5.update(victim_fullpath.encode())
    md5_Digest = md5.hexdigest()

    return md5_Digest
    
        
def run_tests_pv(project,md5, polluter_fullpath, victim_fullpath):
    pv_arg=[polluter_fullpath,victim_fullpath,'--csv',CACHE_DIR+project+'/{}.csv'.format(md5)]
    capture = io.StdCapture()
    pytest.main(pv_arg)
    capture.reset()
    csv_result=pd.read_csv(CACHE_DIR +project+ '/{}.csv'.format(md5))
    status=csv_result['status']
    pv_result=status[len(status)-1]

    return pv_result

def run_tests_pcv(project, md5, polluter_fullpath, cleaner_fullpath, victim_fullpath):
    pcv_arg = [polluter_fullpath,cleaner_fullpath,victim_fullpath, '--csv', CACHE_DIR +project+ '/{}.csv'.format(md5)]
    capture = io.StdCapture()
    pytest.main(pcv_arg)
    capture.reset()
    csv_result = pd.read_csv(CACHE_DIR +project+ '/{}.csv'.format(md5))
    status = csv_result['status']
    pcv_result = status[len(status)-1]

    return pcv_result



if __name__ == "__main__":
    
    project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path, result_path = sys.argv[1:8]
    fix_victim(project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path,result_path)
    
