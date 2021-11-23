# python3 isolated.py dataset_final.csv output

import os
import sys
import csv
import pandas as pd
import traceback

dataset = sys.argv[1]
output_dir = sys.argv[2]
output_csv = os.path.join(output_dir, "victim_or_brittles.csv")
output_victim = os.path.join(output_dir, "victims.csv")
output_brittle = os.path.join(output_dir, "brittles.csv")
output_nod = os.path.join(output_dir, "non-deterministic.csv")
errors = os.path.join(output_dir, "errors_isolated.csv")

TASK = "isolated"
VICTIM = "victim"
BRITTLE = "brittle"

tot = sum(1 for row in csv.reader(open(dataset, 'rt')))
with open(dataset, 'rt') as fds, \
     open(output_csv, 'w') as outputfile, \
     open(output_victim, 'w') as out_victim, \
     open(output_brittle, 'w') as out_brittle, \
     open(output_nod, 'w') as out_nod, \
     open(errors, 'w') as errorfile :

    for i, row in enumerate(csv.reader(fds)):
        print("\r{} / {}".format(i, tot), end="")
        Project = row[0]
        Project_URL = row[1]
        Project_Hash = row[2]
        Test_filename = row[3]
        Test_classname = row[4]
        Test_funcname = row[5]
        Test_parametrization = row[6]
        Verdict_Isolated = row[8]
        if Project == "Project_Name":
            csv.writer(outputfile).writerow(["Project_Name", "Project_URL", "Project_Hash", "Test_id", "Test_Type"])
            csv.writer(out_victim).writerow(["Project_Name", "Project_URL", "Project_Hash", "Test_id", "Verdict", "Consistence"])
            csv.writer(out_brittle).writerow(["Project_Name", "Project_URL", "Project_Hash", "Test_id", "Verdict", "Consistence"])
            csv.writer(out_nod).writerow(["Project_Name", "Project_URL", "Project_Hash", "Test_id", "Verdict", "Consistence"])
            csv.writer(errorfile).writerow(["Project_Name","Project_URL","Project_Hash","Test_filename","Test_classname","Test_funcname",
                                       "Test_parametrization","Order-dependent","Verdict_Isolated","Verdict_OriginalOrder"])
            continue
        if Test_classname != '':
            Test_id = Test_filename + "::" + Test_classname + "::" + Test_funcname + Test_parametrization
        else:
            Test_id = Test_filename + "::"  + Test_funcname + Test_parametrization

        try:
            victim_mapping = dict()
            verdicts = []
            with open(os.path.join(output_dir, TASK, Project, "victim_mapping.csv")) as f1:
                for row1 in csv.reader(f1):
                    victim_mapping[row1[0]] = row1[1]
                for i in os.listdir(os.path.join(output_dir, TASK, Project, victim_mapping[Test_id])):
                    try: 
                        verdicts.append(pd.read_csv(os.path.join(output_dir, TASK, Project, victim_mapping[Test_id], i))['status'][0])
                    except:
                        continue
            verdicts=list(set(verdicts))
            if len(verdicts) == 1:
                csv.writer(outputfile).writerow([Project, Project_URL, Project_Hash, Test_id, 
                    VICTIM if verdicts[0] == "passed" else BRITTLE])
                outwriter = csv.writer(out_victim) if verdicts[0] == "passed" else csv.writer(out_brittle)
                outwriter.writerow([Project, Project_URL, Project_Hash, Test_id, 
                    VICTIM if verdicts[0] == "passed" else BRITTLE, True if verdicts[0].upper() == Verdict_Isolated.upper() else False])
            else:
                csv.writer(out_nod).writerow([Project, Project_URL, Project_Hash, Test_id, Verdict_Isolated, "False"])
                csv.writer(outputfile).writerow([Project, Project_URL, Project_Hash, Test_id, "Non-deterministic"])

        except Exception as e:
            traceback.print_exc()
            csv.writer(errorfile).writerow(row)
            csv.writer(outputfile).writerow([Project, Project_URL, Project_Hash, Test_id, "ERROR"])
            continue
