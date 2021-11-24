import csv

with open("master/Project_status.csv", 'w') as output:
    output.write("Project_Name,Project_URL,Project_Hash,Number_of_Tests_in_Test_Suite,Number_of_Failing_Tests,Time_to_Run_Tests,Number_of_OD_Tests")

valid_projects = []
with open("master/src/victim_or_brittles.csv", 'rt') as dataset:
    for row in csv.reader(dataset):
        if (row[0] == "Project_Name"): continue
        valid_projects.append(row[0])

print(len(set(valid_projects)))

with open("pytest_suites_stat.csv", 'rt') as stat, \
     open("master/Project_status.csv", 'a') as output:
    for row in csv.reader(stat):
        if row[0] == "Project_Name":
            continue
        if row[0] in set(valid_projects):
            csv.writer(output).writerow(row)
