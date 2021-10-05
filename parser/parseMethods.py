import csv
import shutil
import pandas as pd
import os

dataset_dir = "../victims_brittles.csv"
dataset_amended = "../dataset_amended.csv"


def init(resultDir, ErrorLog):
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)
    with open(ErrorLog, 'w') as f:
        csv.writer(f).writerow(['ErrorType', 'Project_Name', 'Test_filename', 'Test_id'])

def init_csv_for_isolated_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 
                                'Test_filename', 'Test_id', 'Verdict_Isolated', 'Conflict'])

def init_csv_for_paired_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 
                                'Test_filename', 'Test1', 'Status1', 
                                'Test2', 'Status2', 'Conflict'])

def init_stat_csv_for_paired_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 'Test_filename', 
                                'Test_id', 'Count', 'Conflict'])

def init_csv_for_triple_tests(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 'Test_filename',
                                'Test1', 'Test2', 'Test3'])

def update_isolated_tests(filename, Project, Test_id, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Project[0], Project[1], Project[2],
                                Project[3], Test_id,
                                TestType[0], TestType[1]])

def update_paired_tests(filename, Project, csvdata, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Project[0], Project[1], Project[2], Project[3],
                                csvdata['id'][0], csvdata['status'][0], 
                                csvdata['id'][1], csvdata['status'][1], TestType])

def update_stat_for_paired_tests(filename, Project, TestId, Count, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Project[0], Project[1], Project[2], Project[3],
                                TestId, Count, TestType])

def update_triple_tests():
    a=1


def Gruber_init():
    Gruber = dict()
    with open(dataset_amended, 'rt') as f:
        r = csv.reader(f)
        for row in r:
            project = row[0]
            Test_filename = row[3]
            Test_classname = row[4]
            Test_funcname = row[5]
            Test_para = row[6]

            if Test_classname != '':
                Test_id = Test_filename + "::" + Test_classname + "::" + Test_funcname + Test_para
            else:
                Test_id = Test_filename + "::"  + Test_funcname + Test_para
            
            Gruber[project+'$'+Test_id] = row
    return Gruber

