#  python3 Test_status.py 

import csv
from functools import reduce
import numpy as np
import pandas as pd

Gruber_flakies = dict()

with open("repro/src/dataset_amended.csv", 'rt') as infile:
    for row in csv.reader(infile):
        Project = row[0]
        Project_URL = row[1]
        Project_Hash = row[2]
        Test_filename = row[3]
        Test_classname = row[4]
        Test_funcname = row[5]
        Test_parametrization = row[6]
        Verdict_Isolated = row[8]
        if Test_classname != '':
            Test_id = Test_filename + "::" + Test_classname + "::" + Test_funcname + Test_parametrization
        else:
            Test_id = Test_filename + "::"  + Test_funcname + Test_parametrization

        Gruber_flakies[Project+Test_id] = "Victim" if Verdict_Isolated == "Passed" else "Brittle"

tests = pd.read_csv("repro/src/victim_or_brittles.csv")
polluters = pd.read_csv("repro/src/polluters.csv")
polluters_stat = pd.read_csv("repro/src/polluters_stat.csv")
cleaners = pd.read_csv("repro/src/cleaners.csv")
statesetters = pd.read_csv("repro/src/state_setters.csv")
statesetters_stat = pd.read_csv("repro/src/state_setters_stat.csv")
patches = pd.read_csv("repro/src/victim_brittle_fix_status.csv")

rand_victim = pd.read_csv("repro/src/random.csv")
rand_brittle = pd.read_csv("repro/src/random.csv")

with open("repro/Test_status.csv", 'w') as output1:
    output1.write("Project_Name,Project_URL,Project_Hash,Test_id,Test_type,Dependent_test,Extra_test,Polluter_Setter_TBD,Consist_Gruber\n")


numODTestsCanRun = 0
numConfirmedVictims = 0
numConfirmedBrittles = 0
numNOD = 0
numDeterm = 0
numDetermPass = 0
numDetermFail = 0
numTimeoutRandom = 0

numVictimsPolluterUnknown = 0
numBrittlesSetterUnknown = 0
numVictimsWithPolluter = 0
numVictimsWithCleaner = 0
numBrittlesWithSetter = 0
numODTestsWithSetterPolluter = 0
numODTestsWithSetterCleaner = 0



with open("repro/Test_status.csv", 'a') as output:
    for i in range(len(tests)):
        Project_Name = tests['Project_Name'][i]
        Project_URL = tests['Project_URL'][i]
        Project_Hash = tests['Project_Hash'][i]
        Test_id = tests['Test_id'][i]

        patch_index = np.where(patches['OD_test_id'] == Test_id)[0]
        if len(patch_index) and patches['fix_status'][patch_index[0]] in \
            ["nondeterministic", "statesetter not works", "cleaner not works"] :
            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, None, None])
            numNOD += 1
            numODTestsCanRun += 1
            continue
       
        if tests['Test_Type'][i] == "victim":
            numODTestsCanRun += 1
            polluters_index = np.where(polluters['Test_id'] == Test_id)[0]
            if not len(polluters_index):
                rand_index = np.where(rand_victim['Test_id'] == Test_id)[0][0]
                if rand_brittle['Test_type'][rand_index] == "pass":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic_pass", None, None, None, None])
                    numDeterm += 1
                    numDetermPass += 1
                if rand_brittle['Test_type'][rand_index] == "fail":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic_fail", None, None, None, None])
                    numDeterm += 1
                    numDetermFail += 1
                elif rand_victim['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, None, None])
                    numNOD += 1
                elif rand_victim['Test_type'][rand_index] == "victim":
                    Consistence = True if Gruber_flakies[Project_Name+Test_id] == "Victim" else False
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", None, None, True, Consistence])
                    numConfirmedVictims += 1
                    numVictimsPolluterUnknown += 1
                elif rand_victim['Test_type'][rand_index] == "Null":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Null", None, None, None, None])
                    numTimeoutRandom += 1

            else:
                has_cleaner = False
                numConfirmedVictims += 1
                numVictimsWithPolluter += 1
                numODTestsWithSetterPolluter += 1
                for polluter in polluters['Polluter'][polluters_index]:
                    cleaners_index = reduce(np.intersect1d, [np.where(cleaners['Victim'] == Test_id)[0], 
                            np.where(cleaners['Polluter'] == polluter)[0]])
                    if len(cleaners_index):
                        has_cleaner = True
                        for cleaner in cleaners['Cleaner'][cleaners_index]:
                            Consistence = True if Gruber_flakies[Project_Name+Test_id] == "Victim" else False
                            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", polluter, cleaner, False, Consistence])
                    else:
                        Consistence = True if Gruber_flakies[Project_Name+Test_id] == "Victim" else False
                        csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", polluter, None, False, Consistence])
                if has_cleaner:
                    numVictimsWithCleaner += 1
                    numODTestsWithSetterCleaner += 1
                
        if tests['Test_Type'][i] == "brittle":
            numODTestsCanRun += 1
            statesetterss_index = np.where(statesetters['Test_id'] == Test_id)[0]
            if not len(statesetterss_index):
                rand_index = np.where(rand_brittle['Test_id'] == Test_id)[0][0]
                if rand_brittle['Test_type'][rand_index] == "pass":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic_pass", None, None, None, None])
                    numDeterm += 1
                    numDetermPass += 1
                if rand_brittle['Test_type'][rand_index] == "fail":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic_fail", None, None, None, None])
                    numDeterm += 1
                    numDetermFail += 1
                elif rand_brittle['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, None, None])
                    numNOD += 1
                elif rand_brittle['Test_type'][rand_index] == "brittle":
                    Consistence = True if Gruber_flakies[Project_Name+Test_id] == "Brittle" else False
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", None, None, True, Consistence])
                    numConfirmedBrittles += 1
                    numBrittlesSetterUnknown += 1
                elif rand_victim['Test_type'][rand_index] == "Null":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Null", None, None, None, None])
                    numTimeoutRandom += 1

            else:
                numConfirmedBrittles += 1
                numBrittlesWithSetter += 1
                numODTestsWithSetterCleaner += 1
                numODTestsWithSetterPolluter += 1
                for statesetter in statesetters['State-setter'][statesetterss_index]:
                    Consistence = True if Gruber_flakies[Project_Name+Test_id] == "Brittle" else False
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", statesetter, None, False, Consistence])                  

        if tests['Test_Type'][i] == "Non-deterministic":
            numODTestsCanRun += 1
            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, None, None])
            numNOD += 1

         
dict_stat = {
    "numODTestsCanRun": numODTestsCanRun,
    "numConfirmedVictims": numConfirmedVictims,
    "numConfirmedBrittles" : numConfirmedBrittles,
    "numNOD" : numNOD,
    "numDeterm" : numDeterm,
    "numDetermPass" : numDetermPass,
    "numDetermFail" : numDetermFail,
    "numTimeoutRandom" : numTimeoutRandom,

    "numVictimsPolluterUnknown" : numVictimsPolluterUnknown,
    "numBrittlesSetterUnknown" : numBrittlesSetterUnknown,
    "numVictimsWithPolluter": numVictimsWithPolluter, 
    "numVictimsWithCleaner" : numVictimsWithCleaner,
    "numBrittleWithSetter" : numBrittlesWithSetter,
    "numODTestsWithSetterPolluter" : numODTestsWithSetterPolluter,
    "numODTestsWithSetterCleaner" : numODTestsWithSetterCleaner
}

for key in dict_stat:
    print("{} : {}".format(key, dict_stat[key]))