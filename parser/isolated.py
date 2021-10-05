from parseMethods import *

output_dir = "../output_archived/isolated"
result_dir = "../parsing_result/isolated"
error_log = os.path.join(result_dir, 'Error.csv')

projects_not_tun = os.path.join(result_dir, 'projects_not_tun.csv')
tests_not_tun = os.path.join(result_dir, 'tests_not_run.csv')

Gruber = Gruber_init()
init(result_dir, error_log)
init_csv_for_isolated_tests(os.path.join(result_dir, 'Inconsistency.csv'))
init_csv_for_isolated_tests(os.path.join(result_dir, 'Victim.csv'))
init_csv_for_isolated_tests(os.path.join(result_dir, 'Brittle.csv'))

f = open(projects_not_tun, 'w')
f.close()
f = open(tests_not_tun, 'w')
f.close()


num_row, num_found, num_project_not_run, num_test_not_run = 0, 0, 0, 0
num_inconsistency, num_match, num_unmatch = 0, 0, 0

for key in Gruber:
    num_row += 1

    row = Gruber[key]
    Project = [row[0], row[1], row[2], row[3]]
    Test_filename = row[3]
    Test_classname = row[4]
    Test_funcname = row[5]
    Test_para = row[6]
    Gruber_Isolated = row[8]

    if Test_classname != '':
        Test_id = Test_filename + "::" + Test_classname + "::" + Test_funcname + Test_para
    else:
        Test_id = Test_filename + "::"  + Test_funcname + Test_para

    Victim_Hash = {}
    if not os.path.exists(os.path.join(output_dir, Project[0])):
        continue
    if not os.path.exists(os.path.join(output_dir, Project[0], 'victim_mapping.csv')):
        num_project_not_run += 1
        with open(projects_not_tun, 'a') as f:
            csv.writer(f).writerow(row)
        continue
    with open(os.path.join(output_dir, Project[0], 'victim_mapping.csv'), 'rt') as f:
        for row1 in f:
            Victim_Hash[row1[:-34]] = row1[-33:-1]
    num_found += 1
    try:
        Victim_md5 = Victim_Hash[Test_id]
    except:
        num_test_not_run += 1
        with open(tests_not_tun, 'a') as f:
            csv.writer(f).writerow(row)
        continue


    Conflict = 'False'
    Consist = ''
    if not os.path.exists(os.path.join(output_dir, Project[0], Victim_md5)) or len(os.listdir(os.path.join(output_dir, Project[0], Victim_md5))) == 0:
        with open(error_log, 'a') as f:
            csv.writer(f).writerow(['NotRun', Project[0], Project[3], Test_id])
        continue

    for Test_index in os.listdir(os.path.join(output_dir, Project[0], Victim_md5)):
        if Test_index == 'timed_out.csv':
            with open(error_log, 'a') as f:
                csv.writer(f).writerow(['TimedOut', Project[0], Project[3], Test_id])
            break

        try: 
            Isolated_Test = pd.read_csv(os.path.join(output_dir, Project[0], Victim_md5, Test_index))
        except:
            print("\n"+Test_id)
            continue
        if str(Gruber_Isolated).lower() != str(Isolated_Test['status'][0]).lower() and Gruber_Isolated != 'NotAnalysed':
            Conflict = 'True'
        if Consist == '':
            Consist = Isolated_Test['status'][0]
        elif Consist != Isolated_Test['status'][0]:
            update_isolated_tests(os.path.join(result_dir, 'Inconsistency.csv'), Project, Test_id, [Consist, Isolated_Test['status'][0]])
            num_inconsistency += 1
            break

    if Conflict == 'True': 
        num_unmatch += 1
    else:
        num_match += 1

    if Isolated_Test['status'][0] == 'passed':
        update_isolated_tests(os.path.join(result_dir, 'Victim.csv'), Project, Test_id, [Consist, Conflict])
    else:
        update_isolated_tests(os.path.join(result_dir, 'Brittle.csv'), Project, Test_id, [Consist, Conflict])

    print("\rValidating tests from Gruber dataset: %d / %d" % (num_row, len(Gruber)), end="")
print("\rValidating tests from Gruber dataset: %d / %d" % (num_row, len(Gruber)))

print("---------------------------------   Summary   ---------------------------------")
print("%d OD tests in Gruber et al.'s dataset" % (len(Gruber)))
print("%d OD tests are not successfully cloned and run" % (num_project_not_run + num_test_not_run))
print("    %d OD tests in projects not associated: check %s" % (num_project_not_run, projects_not_tun))
print("    %d OD tests failed to fetch with pytest: check %s" % (num_test_not_run, tests_not_tun))
print("%d OD tests are successfully cloned and run" % (num_found))
print("    %d OD tests did not compile: check %s" % (num_found - num_inconsistency - num_match - num_unmatch, error_log))
print("    %d OD tests compiled" % (num_inconsistency + num_match + num_unmatch))
print("        %d OD tests do not get the same result when run 10 times in isolation" % (num_inconsistency))
print("        %d OD tests always get the same result when run 10 times" % (num_match + num_unmatch))
print("            %d OD tests match what Gruber et al. found in isolation" % (num_match))
print("            %d OD tests do not match what Gruber et al. found in isolation" % (num_unmatch))


