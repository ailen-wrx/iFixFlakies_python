from parseMethods import *

output_dir = "../output/isolated"
result_dir = "../parsing_result/isolated"
error_log = os.path.join(result_dir, 'Error.csv')


Gruber = Gruber_init()
init(result_dir, error_log)
init_csv_for_isolated_tests(os.path.join(result_dir, 'Inconsistency.csv'))
init_csv_for_isolated_tests(os.path.join(result_dir, 'Victim.csv'))
init_csv_for_isolated_tests(os.path.join(result_dir, 'Brittle.csv'))

num_row = 0
num_inconsistency, num_match, num_unmatch = 0, 0, 0
for key in Gruber:
    num_row += 1

    row = Gruber[key]
    Project = [row[0], row[1], row[2]]
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
    if not os.path.exists(os.path.join(output_dir, Project[0], 'victim_mapping.csv')):
        continue
    with open(os.path.join(output_dir, Project[0], 'victim_mapping.csv'), 'rt') as f:
        for row1 in f:
            Victim_Hash[row1[:-34]] = row1[-33:-1]
    
    try:
        Victim_md5 = Victim_Hash[Test_id]
    except:
        with open(error_log, 'a') as f:
            csv.writer(f).writerow(['NotFound', Project[0], Test_id])
        continue


    Conflict = 'False'
    Consist = ''
    if len(os.listdir(os.path.join(output_dir, Project[0], Victim_md5))) == 0:
        with open(error_log, 'a') as f:
            csv.writer(f).writerow(['NotRun', Project[0], Test_id])
        continue

    for Test_index in os.listdir(os.path.join(output_dir, Project[0], Victim_md5)):
        if Test_index == 'timed_out.csv':
            with open(error_log, 'a') as f:
                csv.writer(f).writerow(['TimedOut', Project[0], Test_id])
            break

        Isolated_Test = pd.read_csv(os.path.join(output_dir, Project[0], Victim_md5, Test_index))
        if str(Gruber_Isolated).lower() != str(Isolated_Test['status'][0]).lower() and Gruber_Isolated != 'NotAnalysed':
            Conflict = 'True'
        if Consist == '':
            Consist = Isolated_Test['status'][0]
        elif Consist != Isolated_Test['status'][0]:
            update_isolated_tests(os.path.join(result_dir, 'Inconsistency.csv'), Project, Isolated_Test, [Consist, Isolated_Test['status'][0]])
            num_inconsistency += 1
            break

    if Conflict == 'True': 
        num_unmatch += 1
    else:
        num_match += 1

    if Isolated_Test['status'][0] == 'passed':
        update_isolated_tests(os.path.join(result_dir, 'Victim.csv'), Project, Isolated_Test, [Consist, Conflict])
    else:
        update_isolated_tests(os.path.join(result_dir, 'Brittle.csv'), Project, Isolated_Test, [Consist, Conflict])

    print("\rValidating tests from Gruber dataset: %d / %d" % (num_row, len(Gruber)), end="")
print("\rValidating tests from Gruber dataset: %d / %d" % (num_row, len(Gruber)))

print("---------------------------------   Summary   ---------------------------------")
print("%d OD tests in Gruber et al.'s dataset" % (len(Gruber)))
print("%d OD tests did not compile" % (len(Gruber) - num_inconsistency - num_match - num_unmatch))
print("    %d OD tests compiled" % (num_inconsistency + num_match + num_unmatch))
print("        %d OD tests do not get the same result when run 10 times in isolation" % (num_inconsistency))
print("        %d OD tests always get the same result when run 10 times" % (num_match + num_unmatch))
print("            %d OD tests match what Gruber et al. found in isolation" % (num_match))
print("            %d OD tests do not match what Gruber et al. found in isolation" % (num_unmatch))


