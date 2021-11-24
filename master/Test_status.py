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

with open("master/Test_status.csv", 'w') as output1:
    output1.write("Project_Name,Project_URL,Project_Hash,Test_id,Test_type,Dependent_test,Extra_test,Unkonwn\n")


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
            continue
       
        if tests['Test_Type'][i] == "victim":
            polluters_index = np.where(polluters['Test_id'] == Test_id)[0]
            if not len(polluters_index):
                rand_index = np.where(rand_victim['Test_id'] == Test_id)[0][0]
                if rand_victim['Test_type'][rand_index] == "DETERMINISTIC":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "victim":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", None, None, True])
                else:
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Null", None, None, False])

            else:
                for polluter in polluters['Polluter'][polluters_index]:
                    cleaners_index = reduce(np.intersect1d, [np.where(cleaners['Victim'] == Test_id)[0], 
                            np.where(cleaners['Polluter'] == polluter)[0]])
                    if len(cleaners_index):
                        for cleaner in cleaners['Cleaner'][cleaners_index]:
                            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", polluter, cleaner, False])
                    else:
                        csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", polluter, None, False])

        if tests['Test_Type'][i] == "brittle":
            statesetterss_index = np.where(statesetters['Test_id'] == Test_id)[0]
            if not len(statesetterss_index):
                rand_index = np.where(rand_victim['Test_id'])[0][0]
                if rand_victim['Test_type'][rand_index] == "DETERMINISTIC":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "brittle":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", None, None, True])
                else:
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Null", None, None, False])

            else:
                for statesetter in statesetters['State-setter'][statesetterss_index]:
                   csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", statesetter, None, False])                  

        if tests['Test_Type'][i] == "Non-deterministic":
            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, None])


                    



