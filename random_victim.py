import json
import csv
import os

dataset = []
projs = []
ProjectsLib = []

with open("master/src/no_polluters.csv", 'rt') as infile:
    for row in csv.reader(infile):
        if row[0] == "Project_Name":
            continue


        Project = row[0]
        Project_URL = row[1]
        Project_Hash = row[2]
        Test_id = row[3]
        
        
        dataset.append([row[0], row[1], row[2], Test_id])
        projs.append(row[0])

with open("master/src/random_victim.csv", 'w') as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,Test_type\n")

valid, deter, nod, od = 0, 0, 0, 0

for data in dataset: 
    Project = data[0]
    Project_URL = data[1]
    Project_Hash = data[2]
    test = data[3]


    with open("master/src/random_victim.csv", 'a') as output:

        if os.path.exists("output/ipflakies_output/{}/ipflakies_result_patch/flakies.json".format(Project)):
            with open("output/ipflakies_output/{}/ipflakies_result_patch/flakies.json".format(Project),'r') as load_f:
                load_dict = json.load(load_f)
                if Project=="marlin":
                    print(load_dict)
                if test in load_dict:
                    valid += 1
                    ProjectsLib.append(Project)
                    print(test, load_dict[test]["type"])
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, load_dict[test]["type"]])
                    if load_dict[test]["type"] == "NOD":
                        nod += 1
                    else:
                        od += 1
                    continue

        if os.path.exists("output/ipflakies_output/{}/flakies.json".format(Project)):
            valid += 1
            ProjectsLib.append(Project)
            with open("output/ipflakies_output/{}/flakies.json".format(Project),'r') as load_f:
                load_dict = json.load(load_f)
                if test in load_dict:
                    print(test, load_dict[test]["type"])
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, load_dict[test]["type"]])
                    if load_dict[test]["type"] == "NOD":
                        nod += 1
                    else:
                        od += 1
                else:
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, "DETERMINISTIC"])
                    deter += 1
        elif os.path.exists("output/ipflakies_output/{}/ipflakies_result/flakies.json".format(Project)):
            valid += 1
            ProjectsLib.append(Project)
            with open("output/ipflakies_output/{}/ipflakies_result/flakies.json".format(Project),'r') as load_f:
                load_dict = json.load(load_f)
                if test in load_dict:
                    print(test, load_dict[test]["type"])
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, load_dict[test]["type"]])
                    if load_dict[test]["type"] == "NOD":
                        nod += 1
                    else:
                        od += 1
                else:
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, "DETERMINISTIC"])
                    deter += 1
        elif os.path.exists("output/ipflakies_output/{}/ifixflakies_result/flakies.json".format(Project)):
            valid += 1
            ProjectsLib.append(Project)
            with open("output/ipflakies_output/{}/ifixflakies_result/flakies.json".format(Project),'r') as load_f:
                load_dict = json.load(load_f)
                if test in load_dict:
                    print(test, load_dict[test]["type"])
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, load_dict[test]["type"]])
                    if load_dict[test]["type"] == "NOD":
                        nod += 1
                    else:
                        od += 1
                else:
                    csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, "DETERMINISTIC"])
                    deter += 1
        else:
            csv.writer(output).writerow([Project, Project_URL, Project_Hash, test, "Null"])
            print(Project, test)

ProjectsLib = list(set(ProjectsLib)) 

with open("summary_random_victim.txt", 'w') as summary_out:
    summary_out.write("{}/{} suspected victims in {}/{} proj. have no polluters\n".format(
        valid, len(dataset), len(ProjectsLib), len(set(projs))))
    summary_out.write("\t{} susp. victims have 1+ failing and 1+ passing order in 100 random orders\n".format(nod+od))
    summary_out.write("\t\t{} susp. victims can reliably fail and pass\n".format(od))
    summary_out.write("\t\t{} susp. victims cannot reliably fail/pass\n".format(nod))
    summary_out.write("\t{} susp. victims have no failing or no passing order in 100 random orders\n".format(deter))


