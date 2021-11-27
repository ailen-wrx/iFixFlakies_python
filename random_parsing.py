import json
import csv
import os

Gruber_flakies = []

dataset = []
projs = []
ProjectsLib = []

TestsInspected = []

with open("repro/src/victims.csv", 'rt') as infile:
    for row in csv.reader(infile):
        if row[0] == "Project_Name":
            continue
        Project = row[0]
        Project_URL = row[1]
        Project_Hash = row[2]
        Test_id = row[3]  
        dataset.append([row[0], row[1], row[2], Test_id])
        if [row[0], row[1], row[2]] not in projs:
            projs.append([row[0], row[1], row[2]])


with open("repro/src/brittles.csv", 'rt') as infile:
    for row in csv.reader(infile):
        if row[0] == "Project_Name":
            continue
        Project = row[0]
        Project_URL = row[1]
        Project_Hash = row[2]
        Test_id = row[3]  
        dataset.append([row[0], row[1], row[2], Test_id])
        if [row[0], row[1], row[2]] not in projs:
            projs.append([row[0], row[1], row[2]])


with open("dataset_amended.csv", 'rt') as infile:
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

        Gruber_flakies.append(Project+Test_id)


with open("repro/src/random.csv", 'w') as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,Test_type\n")

valid, deter, nod, od, deter_pass, deter_fail = 0, 0, 0, 0, 0, 0

for data in dataset: 
    Project = data[0]
    Project_URL = data[1]
    Project_Hash = data[2]
    test = data[3]

    with open("repro/src/random.csv", 'a') as output:
        if os.path.exists("output/ipflakies_output/{}/all_flakies.json".format(Project)) and \
            os.path.exists("output/ipflakies_output/{}/non_flakies.json".format(Project)):
            valid += 1
            ProjectsLib.append(Project)
            with open("output/ipflakies_output/{}/all_flakies.json".format(Project),'r') as load_f, \
                 open("output/ipflakies_output/{}/non_flakies.json".format(Project),'r') as load_nonf:
                load_dict_f = json.load(load_f)
                load_dict_nonf = json.load(load_nonf)
                if test in load_dict_f:
                    print(test, load_dict_f[test]["type"])
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, load_dict_f[test]["type"]])
                    if load_dict_f[test]["type"] == "NOD":
                        nod += 1
                    else:
                        od += 1
                elif test in load_dict_nonf:
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, load_dict_nonf[test]["type"]])
                    deter += 1
                    if load_dict_nonf[test]["type"] == 'pass':
                        deter_pass += 1
                    else:
                        deter_fail += 1
                else:
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, "Null"])
                    print(Project, test)
        else:
            csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, "Null"])
            print(Project, test)

ProjectsLib = list(set(ProjectsLib)) 

with open("summary_random.txt", 'w') as summary_out:
    summary_out.write("{}/{} suspected ODs in {}/{} proj. have no polluters\n".format(
        valid, len(dataset), len(ProjectsLib), len(projs)))
    summary_out.write("\t{} susp. ODs have 1+ failing and 1+ passing order in 100 random orders\n".format(nod+od))
    summary_out.write("\t\t{} susp. ODs can reliably fail and pass\n".format(od))
    summary_out.write("\t\t{} susp. ODs cannot reliably fail/pass\n".format(nod))
    summary_out.write("\t{} susp. ODs have no failing or no passing order in 100 random orders\n".format(deter))



with open("repro/src/MoreFlakies.csv", 'w') as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,Test_type\n")

for row in projs:
    Project = row[0]
    Project_URL = row[1]
    Project_Hash = row[2]
    with open("repro/src/MoreFlakies.csv", 'a') as output:
        if os.path.exists("output/ipflakies_output/{}/all_flakies.json".format(Project)):
            with open("output/ipflakies_output/{}/all_flakies.json".format(Project),'r') as load_f:
                load_dict_f = json.load(load_f)
                for key in load_dict_f:
                    if (Project+key) not in Gruber_flakies:
                        csv.writer(output).writerow([Project, Project_URL, Project_Hash, key, load_dict_f[key]["type"]])
