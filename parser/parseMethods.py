import csv
import pandas as pd
import os

output_dir = "../output"
dataset_dir = "../victims_brittles.csv"
result_dir = "../parsing_result"


def update_isolated_tests(filename, Gruber, Isolated):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Gruber['Project_Name'], Gruber['Project_URL'],
                                Gruber['Project_Hash'], Isolated['id'][0],
                                Isolated['status'][0], Gruber['Isolation']])


def update_paired_tests(filename, Gruber, csvdata, Isolated):
    with open(filename, 'a') as f:
        csv.writer(f).writerow([Gruber['Project_Name'], Gruber['Project_URL'],
                                Gruber['Project_Hash'], csvdata['id'][0],
                                csvdata['message'][0], csvdata['id'][1],
                                csvdata['message'][1], Isolated['status'][0],
                                Gruber['Isolation']])


def parse_output_dir(Gruber_Dataset):
    for project in os.listdir(output_dir):
        if project == '.DS_Store':
            continue

        Victim_Hash = {}
        with open(os.path.join(output_dir, project, 'victim_mapping.csv'), 'rt') as f:
            r = csv.reader(f)
            for row in r:
                Victim_Hash[row[2]] = project + '-' + row[0] + '::' + row[1]

        for Victim_md5 in os.listdir(os.path.join(output_dir, project)):
            if Victim_md5 == 'victim_mapping.csv' or Victim_md5 == '.DS_Store':
                continue

            Isolation_Hash = ''
            try:
                with open(os.path.join(output_dir, project, Victim_md5, 'test_mapping.csv'), 'rt') as f:
                    r = csv.reader(f)
                    for row in r:
                        if row[0] == '':
                            Isolation_Hash = row[2]
                            break
            except Exception as e:
                with open(os.path.join(result_dir, 'Error.log'), 'a') as f:
                    f.write("Error {0}".format(str(e)) + '\n')

            try:
                Gruber_Metadata = Gruber_Dataset.get(Victim_Hash[Victim_md5])
            except:
                continue

            for Test_md5 in os.listdir(os.path.join(output_dir, project, Victim_md5)):
                if Test_md5 == 'test_mapping.csv' or Test_md5 == '.DS_Store':
                    continue

                Isolated_Test = ''
                if Test_md5 == Isolation_Hash + '.csv':
                    Isolated_Test = pd.read_csv(os.path.join(output_dir, project, Victim_md5, Test_md5))
                    Conflict = 0
                    if str(Gruber_Metadata['Isolation']).lower() != str(Isolated_Test['status'][0]).lower() \
                            and Gruber_Metadata['Isolation'] != 'NotAnalysed':
                        Conflict = 1
                    if Conflict:
                        update_isolated_tests(os.path.join(result_dir, 'Conflict_Verdict_Isolated.csv'),
                                              Gruber_Metadata, Isolated_Test)
                    else:
                        if Isolated_Test['status'][0] == 'passed':
                            update_isolated_tests(os.path.join(result_dir, 'Victim_Verdict_Isolated.csv'),
                                                  Gruber_Metadata, Isolated_Test)
                        else:
                            update_isolated_tests(os.path.join(result_dir, 'Brittle_Verdict_Isolated.csv'),
                                                  Gruber_Metadata, Isolated_Test)

                else:
                    try:
                        Paired_Test = pd.read_csv(os.path.join(output_dir, project, Victim_md5, Test_md5))
                        if Paired_Test['status'][0] == 'passed' and Paired_Test['status'][1] == 'passed':
                            update_paired_tests(os.path.join(result_dir, 'Pass-Pass.csv'), Gruber_Metadata,
                                                Paired_Test, Isolated_Test)
                        if Paired_Test['status'][0] == 'passed' and Paired_Test['status'][1] == 'failed':
                            update_paired_tests(os.path.join(result_dir, 'Pass-Fail.csv'), Gruber_Metadata,
                                                Paired_Test, Isolated_Test)
                        if Paired_Test['status'][0] == 'failed' and Paired_Test['status'][1] == 'passed':
                            update_paired_tests(os.path.join(result_dir, 'Fail-Pass.csv'), Gruber_Metadata,
                                                Paired_Test, Isolated_Test)
                        if Paired_Test['status'][0] == 'failed' and Paired_Test['status'][1] == 'failed':
                            update_paired_tests(os.path.join(result_dir, 'Fail-Fail.csv'), Gruber_Metadata,
                                                Paired_Test, Isolated_Test)
                    except:
                        continue
