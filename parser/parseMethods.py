import csv
import shutil
import pandas as pd
import os

dataset_dir = "../victims_brittles.csv"


def init(resultDir, ErrorLog):
    if not os.path.exists(resultDir):
        os.makedirs(resultDir)
    file = open(ErrorLog, 'w')
    file.close()

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

def update_isolated_tests(filename, Gruber, Isolated, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Gruber['Project_Name'], Gruber['Project_URL'],
                                Gruber['Project_Hash'], Isolated['id'][0],
                                TestType[0], TestType[1]])

def update_paired_tests(filename, Gruber, csvdata, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Gruber['Project_Name'], Gruber['Project_URL'], Gruber['Project_Hash'], 
                                csvdata['id'][0], csvdata['status'][0], 
                                csvdata['id'][1], csvdata['status'][1], TestType])

def update_stat_for_paired_tests(filename, Gruber, TestId, Count, TestType):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Gruber['Project_Name'], Gruber['Project_URL'], Gruber['Project_Hash'], 
                                TestId, Count, TestType])

def update_triple_tests():
    a=1


def Gruber_init():
    Gruber = dict()
    with open(dataset_dir, 'rt') as f:
        r = csv.reader(f)
        for row in r:
            func = row[0] + '-' + row[3] + '::' + row[5]
            Gruber[func] = {'Project_Name': row[0],
                            'Project_URL': row[1],
                            'Project_Hash': row[2],
                            'Isolation': row[8]}
    return Gruber

