# python3 parse_result.py ipflakies_result summary

import os
import json
import csv
import sys

result_dir = sys.argv[1]
output_dir = sys.argv[2]
dataset_file = "dataset_amended.csv"

teststatus = "{}/Test_Status.csv".format(output_dir)
minimized = "{}/Minimized.csv".format(output_dir)
patches = "{}/Patches.csv".format(output_dir)
excluded = "{}/Excluded.csv".format(output_dir)
newfound = "{}/New_Found.csv".format(output_dir)


BRI = "brittle"
VIC = "victim"

idflakies = {}
ipflakies = {}
dataset = {}

with open(teststatus, 'w', newline="") as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,Detected,Have_Patch,OD_Type,Polluter_or_Setter,Cleaner\n")
with open(minimized, 'w', newline="") as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,Detected,Have_Patch,OD_Type,Polluter_or_Setter,Cleaner\n")
with open(patches, 'w', newline="") as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,OD_Type,Polluter_or_Setter,Cleaner,Diff,Path\n")
with open(excluded, 'w', newline="") as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,Order-dependent,Verdict_Isolated,Verdict_OriginalOrder,Reason_for_Excluded\n")
with open(newfound, 'w', newline="") as output:
    output.write("Project_Name,Project_URL,Project_Hash,Test_id,OD_Type,Summary\n")


for project in os.listdir(result_dir):
    if not os.path.exists(os.path.join(result_dir, project, "ipflakies_result", "flakies.json")):
        idflakies[project] = None
        continue
    with open(os.path.join(result_dir, project, "ipflakies_result", "flakies.json"), 'rt') as flakies_json:
        load_dict = json.load(flakies_json)
        idflakies[project] = load_dict
    ipflakies[project] = {}
    for flaky_md5 in os.listdir(os.path.join(result_dir, project, "ipflakies_result")):
        if flaky_md5 == "flakies.json":
            continue
        if not os.path.exists(os.path.join(result_dir, project, "ipflakies_result", flaky_md5, "minimized.json")):
            continue
        with open(os.path.join(result_dir, project, "ipflakies_result", flaky_md5, "minimized.json"), 'rt') as minimized_json:
            load_dict = json.load(minimized_json)
            od_test = load_dict["target"]
            ipflakies[project][od_test] = load_dict

installed_projects = []

with open("pytest_suites_stat_w_time.csv", 'rt') as f:
    for row in csv.reader(f):
        installed_projects.append(row[0])

with open(dataset_file, 'rt') as dataset_f:
    for tuple in csv.reader(dataset_f):
        Project_name = tuple[0]
        Project_URL = tuple[1]
        Project_Hash = tuple[2]
        Test_filename = tuple[3]
        Test_classname = tuple[4]
        Test_funcname = tuple[5]
        Test_parametrization = tuple[6]
        Order_dependent = tuple[7]
        Verdict_Isolated = tuple[8]
        Verdict_OriginalOrder = tuple[9]
        if Project_name == "Project_Name":
            continue
        if Test_classname != '':
            Test_id = Test_filename + "::" + Test_classname + "::" + Test_funcname + Test_parametrization
        else:
            Test_id = Test_filename + "::"  + Test_funcname + Test_parametrization

        if Project_name == "chazutsu":
            with open(excluded, 'a', newline="") as output:
                csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, Order_dependent, 
                                             Verdict_Isolated, Verdict_OriginalOrder, "Destroy_Filesystem"])
            continue
        
        if Project_name not in installed_projects:
            with open(excluded, 'a', newline="") as output:
                csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, Order_dependent, 
                                             Verdict_Isolated, Verdict_OriginalOrder, "Fail_to_Install"])
            continue

        if Project_name not in idflakies:
            with open(excluded, 'a', newline="") as output:
                csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, Order_dependent, 
                                             Verdict_Isolated, Verdict_OriginalOrder, "Not_Run"])
            continue

        if idflakies[Project_name] == None:
            with open(excluded, 'a', newline="") as output:
                csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, Order_dependent, 
                                             Verdict_Isolated, Verdict_OriginalOrder, "Fail_to_Install"])
            continue

        if Project_name not in dataset: 
            dataset[Project_name] = []
        dataset[Project_name].append(Test_id)

        detected_by_ipflakies = False
        suggested_type = BRI if Verdict_Isolated == "Failed" else VIC
        flaky_type = ""
        polluters = {}
        setters = {}
        have_patch = False

        if Test_id in idflakies[Project_name]:
            detected_by_ipflakies = True
            flaky_type = idflakies[Project_name][Test_id]["type"]

        if Test_id in ipflakies[Project_name]:
            info = ipflakies[Project_name][Test_id]
            Deter_Type = "passed" if info["type"] == VIC else "failed"
            if not detected_by_ipflakies:
                with open(minimized, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, Deter_Type, "", ""])
                with open(teststatus, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, Deter_Type, False, False])
                continue
            if flaky_type == "": flaky_type = info["type"]
            if flaky_type == VIC:
                polluters = info["polluter"]
            if flaky_type == BRI:
                setters = info["state-setter"]
            have_patch = info["patch"]
        elif detected_by_ipflakies:
            with open(minimized, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, "", ""])
            with open(teststatus, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, False, False])
            continue
        else:
            with open(excluded, 'a', newline="") as output:
                csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, Order_dependent, 
                                             Verdict_Isolated, Verdict_OriginalOrder, "Error"])
            continue

        if flaky_type == VIC:
            if not polluters: 
                with open(minimized, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, "", ""])
                with open(teststatus, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, False, False])
                continue
            has_cleaner = False
            for polluter in polluters:
                cleaners = polluters[polluter]
                if not cleaners:
                    with open(minimized, 'a', newline="") as output:
                        csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, polluter, ""])
                    continue
                has_cleaner = True
                for cleaner in cleaners:
                    with open(minimized, 'a', newline="") as output:
                        csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, polluter, cleaner["cleaner"]])
                    if cleaner["patch"]:
                        patch = cleaner["patch"]
                        with open(patches, 'a', newline="") as output:
                            csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, flaky_type, polluter, cleaner["cleaner"], patch["diff"], "{}/{}".format(Project_name, patch["patch_file"])])
            if has_cleaner:
                with open(teststatus, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, True, True])
            else:
                with open(teststatus, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, True, False])
            continue

        else:
            if not setters:
                with open(minimized, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, "", ""])
                with open(teststatus, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, False, ""])
                continue
            with open(teststatus, 'a', newline="") as output:
                csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, True, ""])
            for setter in setters:
                with open(minimized, 'a', newline="") as output:
                    csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, detected_by_ipflakies, have_patch, flaky_type, setter, ""])
                if setters[setter] and setters[setter][0]["patch"]:
                    patch = setters[setter][0]["patch"]
                    with open(patches, 'a', newline="") as output:
                        csv.writer(output).writerow([Project_name, Project_URL, Project_Hash, Test_id, flaky_type, setter, "", patch["diff"], "{}/{}".format(Project_name, patch["patch_file"])])               

for Project in idflakies:
    if idflakies[Project] == None: continue
    for flaky in idflakies[Project]:
        if flaky == "time":
            continue
        if flaky not in dataset[Project]:
            flaky_info = idflakies[Project][flaky]
            with open(newfound, 'a', newline="") as output:
                csv.writer(output).writerow([Project, Project_URL, Project_Hash, Test_id, flaky_info["type"], os.path.join(Project, result_dir, "flakies.json")])               



# with open("idflakies.json","w") as f:
#     json.dump(idflakies,f)

# with open("ipflakies.json","w") as f:
#     json.dump(ipflakies,f)