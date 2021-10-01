from parseMethods import *

output_dir = "../output/isolated"
result_dir = "../parsing_result/isolated"
error_log = os.path.join(result_dir, 'Error.csv')


Gruber = Gruber_init()
init(result_dir, error_log)
init_csv_for_isolated_tests(os.path.join(result_dir, 'Inconsistency.csv'))
init_csv_for_isolated_tests(os.path.join(result_dir, 'Victim.csv'))
init_csv_for_isolated_tests(os.path.join(result_dir, 'Brittle.csv'))

for project in os.listdir(output_dir):
    if project == 'stat.csv':
        continue

    # mapping victims
    Victim_Hash = {}
    Victim_List = []
    if not os.path.exists(os.path.join(output_dir, project, 'victim_mapping.csv')):
        continue
    with open(os.path.join(output_dir, project, 'victim_mapping.csv'), 'rt') as f:
        r = csv.reader(f)
        for row in r:
            Victim_Info = project + '-' + row[0] + '::' + row[1]
            if Victim_Info not in Victim_List:
                Victim_List.append(Victim_Info)
                Victim_Hash[row[2]] = Victim_Info

    for Victim_md5 in os.listdir(os.path.join(output_dir, project)):
        if Victim_md5 == 'victim_mapping.csv' or Victim_md5 == 'log_pytest.csv':
            continue

        try:
            Gruber_Metadata = Gruber.get(Victim_Hash[Victim_md5])
            if Gruber_Metadata == None:
                continue
        except:
            continue

        Conflict = 'False'
        Consist = ''
        if len(os.listdir(os.path.join(output_dir, project, Victim_md5))) == 0:
            with open(error_log, 'a') as f:
                f.write("NotRun," + Victim_Hash[Victim_md5] + '\n')
            continue

        # Classifying isolated tests
        for Test_index in os.listdir(os.path.join(output_dir, project, Victim_md5)):
            if Test_index == 'timed_out.csv':
                with open(error_log, 'a') as f:
                    f.write("TimeOut," + Victim_Hash[Victim_md5] + '\n')
                break

            Isolated_Test = pd.read_csv(os.path.join(output_dir, project, Victim_md5, Test_index))
            if str(Gruber_Metadata['Isolation']).lower() != str(Isolated_Test['status'][0]).lower() \
                    and Gruber_Metadata['Isolation'] != 'NotAnalysed':
                Conflict = 'True'
            if Consist == '':
                Consist = Isolated_Test['status'][0]
            elif Consist != Isolated_Test['status'][0]:
                update_isolated_tests(os.path.join(result_dir, 'Inconsistency.csv'), Gruber_Metadata, Isolated_Test, [Consist, Isolated_Test['status'][0]])
                break

        if Isolated_Test['status'][0] == 'passed':
            update_isolated_tests(os.path.join(result_dir, 'Victim.csv'), Gruber_Metadata, Isolated_Test, [Consist, Conflict])
        else:
            update_isolated_tests(os.path.join(result_dir, 'Brittle.csv'), Gruber_Metadata, Isolated_Test, [Consist, Conflict])

