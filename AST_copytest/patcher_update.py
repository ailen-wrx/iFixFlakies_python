
"Usage: python3 copy_test.py cleaner_fullpath victim_fullpath combination_path"
import linecache
import ast
import csv
import difflib
from py import io
import re
import os
import sys
import time
import pytest
import pandas as pd
from unparse import Unparser
from io import StringIO
import hashlib, binascii

CACHE_DIR='../patchercache/'
SAVE_DIR='../../SAVE/'

class get_origin_astInfo(ast.NodeVisitor):
    def __init__(self,node):
        self.import_num = 0
        self.body = node.body

    def get_import_num(self):
        for object in self.body:
            if type(object) == ast.Import or type(object) == ast.ImportFrom:
                self.import_num += 1
        return self.import_num

def get_name_splited(test_full_path):
    splited_list=test_full_path.split('::')
    file_path = splited_list[0]
    func_name = splited_list[-1]
    class_name = None
    if '[' and ']' in func_name: # deal with parameters
        start=func_name.index('[')
        end=func_name.index(']')+1
        par=func_name[start:end]
        func_name_no_par=func_name.replace(str(par),"")
        func_name=func_name_no_par
    if len(splited_list)>2:
        class_name=splited_list[-2]
    
    return file_path,class_name,func_name

def get_victim_node(victim_class, tree_victim, victim_testfunc):
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
        
        return victim_node


def get_helper_code(cleaner_testfunc,tree_cleaner,cleaner_class):
    # get helper code from cleaner, handle setup, body and teardown 'module, method, class, function'
        # setup_module,setup_class,setup_function,setup_method,test_body,teardown_method,teardown_function,teardown_class,teardown_module

    #name_node_dict = {'setup_module': None, 'setUpClass': None, 'setup_function': None, 'setup_method': None,
    #                      cleaner_testfunc: None,
    #                      'teardown_method': None, 'teardown_function': None, 'tearDownClass': None,
    #                      'teardown_module': None}
    helper_node_dict={'setup' : None, cleaner_testfunc : None, 'teardown' : None}
    setup_pattern = re.compile(r'setup', re.IGNORECASE)
    teardown_pattern = re.compile(r'teardown', re.IGNORECASE)

    if cleaner_class:
           for clean_class in [node for node in ast.walk(tree_cleaner) if isinstance(node, ast.ClassDef)]:
               if clean_class.name == cleaner_class:
                   for clean_obj in [func for func in ast.iter_child_nodes(clean_class) if isinstance(func, ast.FunctionDef)]:     
                        #if clean_obj.name in name_node_dict:
                        #    name_node_dict[clean_obj.name] = clean_obj.body
                        if re.search(setup_pattern, clean_obj.name):
                            helper_node_dict['setup'] = clean_obj.body
                        if re.search(teardown_pattern, clean_obj.name):
                            helper_node_dict['teardown'] = clean_obj.body
                        if clean_obj.name == cleaner_testfunc:
                            helper_node_dict[cleaner_testfunc] = clean_obj.body
                   break


           insert_nodes_keys = [key for key in helper_node_dict if helper_node_dict[key] != None]
           pre_node_key = insert_nodes_keys[0]
           pre_node = helper_node_dict[pre_node_key]

           if len(insert_nodes_keys) > 1:
               for key in insert_nodes_keys[1:]:
                   helper_node_dict[key].insert(0, pre_node)
                   pre_node = helper_node_dict[key]
           insert_node = pre_node

    else:
            for eachfunc in [func for func in ast.walk(tree_cleaner) if isinstance(func, ast.FunctionDef)]:
                if eachfunc.name in helper_node_dict:
                    if re.search(setup_pattern, eachfunc.name):
                        helper_node_dict['setup'] = eachfunc.body
                    if re.search(teardown_pattern, eachfunc.name):
                        helper_node_dict['teardown'] = eachfunc.body
                    if eachfunc.name == cleaner_testfunc:
                        helper_node_dict[cleaner_testfunc] = eachfunc.body

            insert_nodes_keys = [key for key in helper_node_dict if helper_node_dict[key] != None]

            pre_node_key = insert_nodes_keys[0]
            pre_node = helper_node_dict[pre_node_key]

            if len(insert_nodes_keys) > 1:
                print(insert_nodes_keys)
                for key in insert_nodes_keys[1:]:
                     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',key)
                     helper_node_dict[key].insert(0, pre_node)
                     pre_node = helper_node_dict[key]
            insert_node = pre_node

            print(insert_node)
    return insert_node


def fix_victim(project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path,result_path):

    cache_in_tests=[]
    patch_list=[]

    final_patch_content=''

    diff=None
    diff_right=None
    patch_name=None

    victim_path, victim_class, victim_testfunc = get_name_splited(victim_fullpath)
    cleaner_path, cleaner_class, cleaner_testfunc = get_name_splited(cleaner_fullpath)

    
    with open(victim_path, "r") as victim:
        tree_victim = ast.parse(victim.read())
       
    with open(cleaner_path, "r") as cleaner:
        tree_cleaner = ast.parse(cleaner.read())
        cleaner_info = get_origin_astInfo(tree_cleaner)

    md5 = get_md5(polluter_fullpath, cleaner_fullpath, victim_fullpath)


    try:
        pcv_result=run_tests_pcv(project, md5, polluter_fullpath, cleaner_fullpath, victim_fullpath)
        pv_result=run_tests_pv(project, md5,polluter_fullpath,victim_fullpath)

    except:
        with open(result_path,'a+') as f:
            csv_write = csv.writer(f)
            result=[project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5,'PCV_PV_ERROR']
            csv_write.writerow(result)
            exit(1)
            
    minimal_patch_file=None
    patch_time = None
    can_copy_work = None
    can_patch_work = None

    patch_time_all= None
    import_obj_list=[]
    
    if pv_result != 'passed' and pcv_result =='passed':

        # copy unique Import and ImportFrom modules
        for import_obj in [module for module in ast.walk(tree_cleaner) if
                           isinstance(module, ast.Import) or isinstance(module, ast.ImportFrom)]:
            if ast.dump(import_obj) not in [ast.dump(module) for module in ast.walk(tree_victim) if
                                            isinstance(module, ast.Import) or isinstance(module, ast.ImportFrom)]:
                tree_victim.body.insert(0, import_obj)
                import_obj_list.append(import_obj)
     
                
        insert_node=get_helper_code(cleaner_testfunc,tree_cleaner,cleaner_class) 
        victim_node = get_victim_node(victim_class, tree_victim, victim_testfunc)

        victim_start_lineno = victim_node[0].lineno


        tmp_insert_node = insert_node
        tmp_tree_victim = tree_victim
        victim_node.insert(0, tmp_insert_node)
        ast.fix_missing_locations(tmp_tree_victim)


        insert_buf = StringIO()
        Unparser(tmp_insert_node, insert_buf)
        insert_buf.seek(0)
        tmp_content = insert_buf.read()

        try:
            buf = StringIO()
            Unparser(tmp_tree_victim, buf)
            buf.seek(0)
            edited_content = buf.read()
            
        except IndentationError:
            can_copy_work=False
            with open(result_path,'a+') as f:
                csv_write = csv.writer(f)
                result=[project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5,'insert error']
                csv_write.writerow(result)
            exit(1)

        with open(combination_path, "w") as combination:
            combination.write(edited_content)
        result = (run_tests_pv(project, md5, polluter_fullpath,
                               combination_path + '::' + '::'.join(victim_fullpath.split('::')[1:])))

        victim_node.remove(tmp_insert_node)
        patch_num = 0
        patch_time = None
        patch_time_all = None
        minimal_patch_file= None
        start_time = time.perf_counter()

        can_copy_work = False
        if result == 'passed':
            can_copy_work = True
            minimal_patch_file=combination_path
            patch_list.append(tmp_content)

        # minimize code by delta debugging
        n = 2
        roundnum=0

        while len(tmp_insert_node) >= 2:
            start = 0
            subset_length = len(tmp_insert_node) // n
            pollution_is_cleaned = False
            while start < len(tmp_insert_node):
                this_round_insert_list = tmp_insert_node[:start] + tmp_insert_node[start + subset_length:]

                #tmp_tree_victim = origin_tree_victim
                #tmp_victim_node = victim_node

                try:
                    victim_node.insert(0, this_round_insert_list)
                    ast.fix_missing_locations(tmp_tree_victim)
                    can_be_inserted=True

                except:# IndentationError:
                    can_be_inserted=False

                    with open(result_path,'a+') as f:
                        csv_write = csv.writer(f)
                        result=[project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5,'insert error']
                        csv_write.writerow(result)
                    exit(1)
                tmp_buf = StringIO()
                Unparser(this_round_insert_list, tmp_buf)
                tmp_buf.seek(0)
                tmp_content = tmp_buf.read()

                print(tmp_content)
                print('~~~~~~~~~~~~~~~')
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
                    victim_node.remove(this_round_insert_list)
                can_patch_work=(run_tests_pv(project,md5, polluter_fullpath, combination_path + '::' + '::'.join(victim_fullpath.split('::')[1:])))

                cache_in_tests.append(combination_path)

                print(can_patch_work)
                if can_patch_work == 'passed':
                    patch_time = time.perf_counter()
                    patch_num += 1
                    if patch_num == 1:
                        patch_time = patch_time - start_time
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CAN BE A PATCH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n',tmp_content)
                    minimal_patch_file=combination_path
                    patch_list.append(tmp_content)
                    tmp_insert_node = this_round_insert_list
                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@',len(tmp_insert_node))
                    n = max(n - 1, 2)
                    pollution_is_cleaned = True
                    break
                start = start + subset_length
            if not pollution_is_cleaned:
                n = min(n * 2, len(tmp_insert_node))
                if n == len(tmp_insert_node):
                    break
        end_time = time.perf_counter()
        if can_patch_work == 'passed':
            patch_time_all = end_time - start_time


    if minimal_patch_file:
        insert_patch_to = victim_start_lineno-1
        processed_patch_file = minimal_patch_file.replace('patch','processedpatch')
        with open(victim_path, "r") as f:
             org_contents = f.readlines()

        with open(minimal_patch_file, "r") as patch:
            tree_patch = ast.parse(patch.read())

        if victim_class:
            for patched_vic_class in [node for node in ast.walk(tree_patch) if isinstance(node,ast.ClassDef)]:
                if patched_vic_class.name == victim_class:
                    for victim_obj in [func for func in ast.iter_child_nodes(patched_vic_class) if isinstance(func,ast.FunctionDef)]:           
                        if victim_obj.name == victim_testfunc:
                               patched_victim_node = victim_obj
                               break

        else:
            for victim_obj in [func for func in ast.walk(tree_patch) if isinstance(func, ast.FunctionDef)]:
                if victim_obj.name == victim_testfunc:
                    patched_victim_node = victim_obj
                    break

        final_patch=[]
        tmp_content = patch_list[-1]
        patch_offset=0
        for each in tmp_content.split('\n'):
            if each !='':
                patch_offset+=1

        for num in range(1,patch_offset+1):
            result =linecache.getline(minimal_patch_file,patched_victim_node.lineno+num)
            final_patch.append(result)


        org_contents.insert(insert_patch_to,''.join(final_patch))
        buf =  StringIO()
        if len(import_obj_list):
            for each in import_obj_list:
                Unparser(each,buf)
                buf.seek(0)
                org_contents.insert(0,buf.read())

        contents = "".join(org_contents)
        with open(processed_patch_file, "w") as fnew:
            fnew.write(contents)
            
        diff=os.popen('diff '+victim_path+' '+processed_patch_file).read()
        print(diff)
        diff_right=run_tests_pv(project,md5, polluter_fullpath,processed_patch_file)

        if diff:
                patch_name="{}{}_patch_{}_.patch".format(SAVE_DIR, victim_testfunc[:(victim_fullpath.index('.'))],md5)
                os.popen('diff -up ' + victim_path+' '+processed_patch_file+ ' > '+patch_name) 
        print(victim_path,processed_patch_file)
        
    with open(result_path,'a+') as f:
        csv_write = csv.writer(f)
        result=[project,sha,polluter_fullpath,cleaner_fullpath,victim_fullpath,md5,pv_result,pcv_result,can_copy_work,patch_time_all,patch_name]

        #for each in patch_list:
        #    result.append(each)
        result.append(diff)
        result.append(diff_right)

        if len(patch_list):
           result.append(patch_list[-1])
           
        csv_write.writerow(result)
        
    for each in cache_in_tests:
        if each != minimal_patch_file:
            os.remove(each)

def generate_diff(original_victim,fixed_victim):

    original_victim_file=open(original_victim,'r')
    fixed_victim_file=open(fixed_victim,'r')
    diff=difflib.ndiff(original_victim_file.readlines(),fixed_victim_file.readlines())

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~`')
    print('\n'.join(list(diff)))
    delta= ''.join(x[2:] for x in diff if x.startswith('- '))

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

    return pv_result.strip()

def run_tests_pcv(project, md5, polluter_fullpath, cleaner_fullpath, victim_fullpath):
    pcv_arg = [polluter_fullpath,cleaner_fullpath,victim_fullpath, '--csv', CACHE_DIR +project+ '/{}.csv'.format(md5)]
    capture = io.StdCapture()
    pytest.main(pcv_arg)
    capture.reset()
    csv_result = pd.read_csv(CACHE_DIR +project+ '/{}.csv'.format(md5))
    status = csv_result['status']
    pcv_result = status[len(status)-1]

    return pcv_result.strip()


if __name__ == "__main__":
    
    project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path, result_path = sys.argv[1:8]

    fix_victim(project,sha,polluter_fullpath, cleaner_fullpath, victim_fullpath, combination_path,result_path)
