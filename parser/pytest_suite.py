
from parseMethods import *

repo_dir = "../Repo"
output_dir = "../pytest_output"
result_dir = "../pytest_suites_stat.csv"
log_dir = "../pytest_suites_log.csv"
dataset_latest = "../dataset_latest.csv"

with open(result_dir, 'w') as f:
    csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 'Number_of_Tests_in_Test_Suite',
                            'Number_of_Failing_Tests', 'Time_to_Run_Tests', 'Number_of_OD_Tests'])

with open(log_dir, 'w') as f:
    csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 'pytest_Status'])
    
with open(dataset_latest, 'w') as f:
    csv.writer(f).writerow(
        ['Project_Name', 'Project_URL', 'Project_Hash', 'Test_filename', 'Test_classname', 'Test_funcname',
         'Test_parametrization', 'Order-dependent', 'Verdict_Isolated', 'Verdict_OriginalOrder'])

Project_Info = dict()
OD_count = dict()
with open(dataset_amended, 'rt') as f:
    r = csv.reader(f)
    for row in r:
        Project_Name = row[0]
        if Project_Name == 'Project_Name':
            continue
        if os.path.exists(os.path.join(output_dir, Project_Name, "pytest.csv")):
            #print("notfound", Project_Name)
            #continue
            with open(dataset_latest, 'a') as f1:
                csv.writer(f1).writerow(row)
        if Project_Name not in Project_Info:
            Project_Info[Project_Name] = row
        if Project_Name not in OD_count:
            OD_count[Project_Name] = 1
        else:
            OD_count[Project_Name] += 1

cnt = 0
for key in Project_Info:
    Project_Name = Project_Info[key][0]
    Project_URL = Project_Info[key][1]
    Project_Hash = Project_Info[key][2]

    if not os.path.exists(os.path.join(repo_dir, Project_Name)):
        #print("not_found", Project_Name)
        with open(log_dir, 'a') as f1:
            csv.writer(f1).writerow([Project_Name, Project_URL, Project_Hash, "Project_Not_Found"])
        continue
    if os.path.exists(os.path.join(output_dir, Project_Name, "timeout")):
        with open(log_dir, 'a') as f1:
            csv.writer(f1).writerow([Project_Name, Project_URL, Project_Hash, "Time_Out"])
        #print("time_out", Project_Name)
        continue
    if not os.path.exists(os.path.join(output_dir, Project_Name)):
        print("not_tested", Project_Name)
        continue
    if not os.path.exists(os.path.join(output_dir, Project_Name, "pytest.csv")):
        with open(log_dir, 'a') as f1:
            csv.writer(f1).writerow([Project_Name, Project_URL, Project_Hash, "Fail_to_Fetch_Tests"])
        #print("test_error", Project_Name)
        continue

    with open(log_dir, 'a') as f1:
        csv.writer(f1).writerow([Project_Name, Project_URL, Project_Hash, "Success"])
    cnt += 1
    Test_Suite = pd.read_csv(os.path.join(output_dir, Project_Name, "pytest.csv"))
    Number_of_Tests_in_Test_Suite = len(Test_Suite['id'])
    Number_of_Failing_Tests = len([status for status in Test_Suite['status'] if status != "passed"])
    Time_to_Run_Tests = sum(Test_Suite['duration'])
    Number_of_OD_Tests = OD_count[Project_Name]

    with open(result_dir, 'a') as f1:
        csv.writer(f1).writerow([Project_Name, Project_URL, Project_Hash, Number_of_Tests_in_Test_Suite, 
                                 Number_of_Failing_Tests, Time_to_Run_Tests, Number_of_OD_Tests])
    #print(Project_Name, Number_of_Tests_in_Test_Suite, Number_of_Failing_Tests, Time_to_Run_Tests, Number_of_OD_Tests)

print (len(Project_Info))
print(cnt)

