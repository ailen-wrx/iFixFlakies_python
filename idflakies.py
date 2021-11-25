import json
import shutil
from bidict import bidict
import csv
import os

OUTPUT_DIR = "output/ipflakies_output"

def seq_encoding(test_dict, seq):
    encoded = []
    for test in seq:
        encoded.append(str(test_dict.inverse[test]))
    return ",".join(encoded)

def seq_decoding(test_dict, list):
    decoded = []
    for index in list.split(","):
        decoded.append(str(test_dict[int(index)]))
    return decoded

def pytestcsv(file):
    res = dict()
    COLUMNS = ['id','module','name','file','doc','markers','status','message','duration']
    with open(file, 'rt') as f:
        for row in csv.reader(f):
            if row[0] == 'id':
                for i in range(len(COLUMNS)):
                    res[COLUMNS[i]] = []
            else:
                for i in range(len(COLUMNS)):
                    res[COLUMNS[i]].append(row[i])
    return res

for project in os.listdir(OUTPUT_DIR):

    print(project)

    all_flakies = dict()
    timeout_project = []
# clean
    if os.path.exists(os.path.join(OUTPUT_DIR, project, 'ipflakies_result_patch', 'flakies.json')):
        with open (os.path.join(OUTPUT_DIR, project, 'ipflakies_result_patch', 'flakies.json'), 'rt') as load_f:
            load_dict = json.load(load_f)
            has_flaky_output = True
            for key in load_dict:
                if key not in all_flakies:
                    all_flakies[key] = load_dict[key]
    if os.path.exists(os.path.join(OUTPUT_DIR, project, 'random_suite', 'normal.csv')):
        os.remove(os.path.join(OUTPUT_DIR, project, 'random_suite', 'normal.csv'))
    has_flaky_output = False
    try:
        if os.path.exists(os.path.join(OUTPUT_DIR, project, 'ifixflakies_result', 'flakies.json')):
            with open (os.path.join(OUTPUT_DIR, project, 'ifixflakies_result', 'flakies.json'), 'rt') as load_f:
                load_dict = json.load(load_f)
                has_flaky_output = True
                for key in load_dict:
                    if key not in all_flakies:
                        all_flakies[key] = load_dict[key]
        if os.path.exists(os.path.join(OUTPUT_DIR, project, 'flakies.json')):
            with open (os.path.join(OUTPUT_DIR, project, 'flakies.json'), 'rt') as load_f:
                load_dict = json.load(load_f)
                has_flaky_output = True
                for key in load_dict:
                    if key not in all_flakies:
                        all_flakies[key] = load_dict[key]
        if os.path.exists(os.path.join(OUTPUT_DIR, project, 'ipflakies_result', 'flakies.json')):
            with open (os.path.join(OUTPUT_DIR, project, 'ipflakies_result', 'flakies.json'), 'rt') as load_f:
                load_dict = json.load(load_f)
                has_flaky_output = True
                for key in load_dict:
                    if key not in all_flakies:
                        all_flakies[key] = load_dict[key]
    except:
        print("!"+project)
    if not has_flaky_output:
        print(project, "Timeout")
        timeout_project.append(project)

# collect
    results = []
    try:
        for t in os.listdir(os.path.join(OUTPUT_DIR, project, 'random_suite')):
            random_test = pytestcsv(os.path.join(OUTPUT_DIR, project, 'random_suite', t))
            results.append(random_test)
        test_list = random_test['id']
    except:
        print(project, "ERROR")
        shutil.rmtree(os.path.join(OUTPUT_DIR, project))
        continue

# process
    try:

        test_dict = bidict()
        non_flakies = dict()
        for index, test in enumerate(test_list):
            test_dict[index] = test

        passing = {}
        failing = {}
        for test in test_list:
            passing[test] = []
            failing[test] = []

        for random_suite in results:
            for index, testid in enumerate(random_suite['id']):
                if random_suite['status'][index] == 'passed':
                    passing[testid].append(seq_encoding(test_dict, random_suite['id'][:index+1]))
                else:
                    failing[testid].append(seq_encoding(test_dict, random_suite['id'][:index+1]))

        for test in test_list:
            if test in all_flakies:
                continue
            set_passing = set(passing[test])
            set_failing = set(failing[test])
            intersection = set_passing.intersection(set_failing)
            NOD = False
            if intersection:
                NOD = True
                failing_seq = []
                for i in list(intersection):
                    failing_seq.append(seq_decoding(test_dict, i))
                all_flakies[test] = { "type": "NOD", 
                                "detected_sequence": failing_seq }
                continue
            if not set_failing:
                non_flakies[test] = { "type": "pass" }
            if not set_passing:
                non_flakies[test] = { "type": "fail" }
    
    except:
        print(project, "[ EXCEPTION ]")

    with open(os.path.join(OUTPUT_DIR, project, 'all_flakies.json'), 'w') as f:
        json.dump(all_flakies, f)

    with open(os.path.join(OUTPUT_DIR, project, 'non_flakies.json'), 'w') as f:
        json.dump(non_flakies, f)
