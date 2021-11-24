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

rand_victim = pd.read_csv("master/src/random_victim.csv")

with open("master/Test_status.csv", 'w') as output1:
    output1.write("Project_Name,Project_URL,Project_Hash,Test_id,Test_type,Dependent_test,Extra_test,Unkonwn\n")


with open("master/Test_status.csv", 'a') as output:
    for i in range(len(tests)):
        Project_Name = tests['Project_Name'][i]
        Project_URL = tests['Project_URL'][i]
        Project_Hash = tests['Project_Hash'][i]
        Test_id = tests['Test_id'][i]

        # print(Project_Name, Test_id)

        if tests['Test_Type'][i] == "Non-deterministic":
            csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, None])
        
        if tests['Test_Type'][i] == "victim":
            polluters_index = np.where(polluters['Test_id'] == Test_id)[0]
            if not len(polluters_index):
                rand_index = np.where(rand_victim['Test_id'] == Test_id)[0][0]
                if rand_victim['Test_type'][rand_index] == "Null": continue
                if rand_victim['Test_type'][rand_index] == "DETERMINISTIC":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "victim":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Victim", None, None, True])

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
                if rand_victim['Test_type'][rand_index] == "Null": continue
                if rand_victim['Test_type'][rand_index] == "DETERMINISTIC":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "NOD":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Non-deterministic", None, None, False])
                elif rand_victim['Test_type'][rand_index] == "brittle":
                    csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", None, None, True])

            else:
                for statesetter in statesetters['State-setter'][statesetterss_index]:
                   csv.writer(output).writerow([Project_Name, Project_URL, Project_Hash, Test_id, "Brittle", statesetter, None, False]) 
                    


                    



