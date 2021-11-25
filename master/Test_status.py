#  python3 master/Test_status.py 

import csv
from functools import reduce
import numpy as np
import pandas as pd

tests = pd.read_csv("master/src/victim_or_brittles.csv")
polluters = pd.read_csv("master/src/polluters.csv")
polluters_stat = pd.read_csv("master/src/polluters_stat.csv")
cleaners = pd.read_csv("master/src/cleaners.csv")
statesetters = pd.read_csv("master/src/state_setters.csv")
statesetters_stat = pd.read_csv("master/src/state_setters_stat.csv")
patches = pd.read_csv("master/src/victim_brittle_fix_status.csv")

rand_victim = pd.read_csv("master/src/random_victim.csv")
rand_brittle = pd.read_csv("master/src/random_brittle.csv")

with open("master/Test_status.csv", 'w') as output1:
    output1.write("Project_Name,Project_URL,Project_Hash,Test_id,Test_type,Dependent_test,Extra_test,Unkonwn\n")


numODTestsCanRun = 0
numConfirmedVictims = 0
numConfirmedBrittles = 0
numNOD = 0
numDeterm = 0
numTimeoutRandom = 0

numVictimsPolluterUnknown = 0
numBrittlesSetterUnknown = 0
numVictimsWithPolluter = 0
numVictimsWithCleaner = 0
numBrittlesWithSetter = 0
numODTestsWithSetterPolluter = 0
numODTestsWithSetterCleaner = 0



with open("master/Test_status.csv", 'a') as output:
    for i in range(len(tests)):
        Project_Name = tests['Project_Name'][i]
        Project_URL = tests['Project_URL'][i]
        Project_Hash = tests['Project_Hash'][i]
        Test_id = tests['Test_id'][i]

        patch_index = np.where(patches['OD_test_id'] == Test_id)[0]
        if len(patch_index) and patches['fix_status'][patch_index[0]] in \
            ["nondeterministic", "statesetter not works", "cleaner not works"] :
            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
            numNOD += 1
            numODTestsCanRun += 1
            continue
       
        if tests['Test_Type'][i] == "victim":
            numODTestsCanRun += 1
            polluters_index = np.where(polluters['Test_id'] == Test_id)[0]
            if not len(polluters_index):
                rand_index = np.where(rand_victim['Test_id'] == Test_id)[0][0]
                if rand_victim['Test_type'][rand_index] == "DETERMINISTIC":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic", None, None, False])
                    numDeterm += 1
                elif rand_victim['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
                    numNOD += 1
                elif rand_victim['Test_type'][rand_index] == "victim":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", None, None, True])
                    numConfirmedVictims += 1
                    numVictimsPolluterUnknown += 1
                else:
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Null", None, None, False])
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
                            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", polluter, cleaner, False])
                    else:
                        csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", polluter, None, False])
                if has_cleaner:
                    numVictimsWithCleaner += 1
                    numODTestsWithSetterCleaner += 1
                
        if tests['Test_Type'][i] == "brittle":
            numODTestsCanRun += 1
            statesetterss_index = np.where(statesetters['Test_id'] == Test_id)[0]
            if not len(statesetterss_index):
                rand_index = np.where(rand_brittle['Test_id'] == Test_id)[0][0]
                if rand_brittle['Test_type'][rand_index] == "DETERMINISTIC":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic", None, None, False])
                    numDeterm += 1
                elif rand_brittle['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
                    numNOD += 1
                elif rand_brittle['Test_type'][rand_index] == "brittle":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", None, None, True])
                    numConfirmedBrittles += 1
                    numBrittlesSetterUnknown += 1
                else:
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Null", None, None, False])
                    numTimeoutRandom += 1

            else:
                numConfirmedBrittles += 1
                numBrittlesWithSetter += 1
                numODTestsWithSetterCleaner += 1
                numODTestsWithSetterPolluter += 1
                for statesetter in statesetters['State-setter'][statesetterss_index]:
                   csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", statesetter, None, False])                  

        if tests['Test_Type'][i] == "Non-deterministic":
            numODTestsCanRun += 1
            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
            numNOD += 1

         
dict_stat = {
    "numODTestsCanRun": numODTestsCanRun,
    "numConfirmedVictims": numConfirmedVictims,
    "numConfirmedBrittles" : numConfirmedBrittles,
    "numNOD" : numNOD,
    "numDeterm" : numDeterm,
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