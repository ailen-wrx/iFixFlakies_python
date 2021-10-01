import csv
import shutil
import pandas as pd
import os

dataset_dir = "../victims_brittles.csv"


def init(resultDir, ErrorLog):
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)
    with open(ErrorLog, 'w') as f:
        csv.writer(f).writerow(['ERROR', 'Project_Name', 'Project_URL', 'Project_Hash', 'Test_id',])

def init_csv_for_isolated_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 
                                'Test_id', 'Verdict_Isolated', 'Conflict'])

def init_csv_for_paired_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 
                                'Test1', 'Status1', 
                                'Test2', 'Status2', 'Conflict'])

def init_stat_csv_for_paired_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 'Test_id', 'Count', 'Conflict'])

def init_csv_for_triple_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 
                                'Test1', 'Test2', 'Test3'])

def update_isolated_tests(filename, Project, Isolated, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Project[0], Project[1],
                                Project[2], Isolated['id'][0],
                                TestType[0], TestType[1]])

def update_paired_tests(filename, Project, csvdata, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Project[0], Project[1], Project[2], 
                                csvdata['id'][0], csvdata['status'][0], 
                                csvdata['id'][1], csvdata['status'][1], TestType])

def update_stat_for_paired_tests(filename, Project, TestId, Count, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Project[0], Project[1], Project[2], 
                                TestId, Count, TestType])

def update_triple_tests():
    a=1


def Gruber_init():
    Gruber = dict()
    with open(dataset_dir, 'rt') as f:
        r = csv.reader(f)
        for row in r:
            project = row[0]
            Test_filename = row[3]
            Test_classname = row[4]
            Test_funcname = row[5]
            Test_para = row[6]

            if str(Test_filename).split('/')[-1] != (str(Test_classname).split('.')[-1] + '.py'):
                Test_id = Test_filename + "::" + str(Test_classname).split('.')[-1] + "::" + Test_funcname + Test_para
            else:
                Test_id = Test_filename + "::"  + Test_funcname + Test_para
            
            Gruber[project+'$'+Test_id] = row
    return Gruber

