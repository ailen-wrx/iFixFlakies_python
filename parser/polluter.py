from parseMethods import *
import sys

output_dir = "../output/polluter"
victim_brittle="../parsing_result/isolated"
result_dir = "../parsing_result/polluter"
error_log = os.path.join(result_dir, 'Error.csv')


Gruber = Gruber_init()
init(result_dir, error_log)

def update(victim_or_brittle):
    test_list = os.path.join(victim_brittle, 'Brittle.csv') if victim_or_brittle == "Brittle" else os.path.join(victim_brittle, 'Victim.csv')
    result_csv = os.path.join(result_dir, 'state-setter-potential.csv') if victim_or_brittle == "Brittle" else os.path.join(result_dir, 'polluter-potential.csv')
    stat_csv = os.path.join(result_dir, 'state-setter-stat-potential.csv') if victim_or_brittle == "Brittle" else os.path.join(result_dir, 'polluter-stat-potential.csv')
    Info = "Detecting state-setters for brittles: " if victim_or_brittle == "Brittle" else "Detecting polluters for victims: "
    init_csv_for_paired_tests(result_csv)
    init_stat_csv_for_paired_tests(stat_csv)
    total = sum(1 for line in open(test_list))
    with open(test_list, 'rt') as f:
        numrow = 0
        r = csv.reader(f)
        for row in r:
            numrow = numrow + 1
            project, Test_id, Conflict = row[0], row[3], row[5]
            Victim_Hash = {}
            Victim_List = []
            if not os.path.exists(os.path.join(output_dir, project, 'victim_mapping.csv')):
                continue
            with open(os.path.join(output_dir, project, 'victim_mapping.csv'), 'rt') as f:
                r1 = csv.reader(f)
                for row1 in r1:
                    Victim_Info = project + '-' + row1[0] + '::' + row1[1]
                    if Victim_Info not in Victim_List:
                        Victim_List.append(Victim_Info)
                        Victim_Hash[row1[2]] = Victim_Info
             
            for Victim_md5 in os.listdir(os.path.join(output_dir, project)):
                match = 1
                if Victim_md5 == 'victim_mapping.csv' or Victim_md5 == 'log_pytest.csv':
                    continue

                try:
                    Gruber_Metadata = Gruber.get(Victim_Hash[Victim_md5])
                    if Gruber_Metadata == None:
                        continue
                except:
                    continue

                count = 0
                if len(os.listdir(os.path.join(output_dir, project, Victim_md5))) == 0:
                    with open(error_log, 'a') as f:
                        f.write("NotRun," + Victim_Hash[Victim_md5] + '\n')
                    continue
                for Test_md5 in os.listdir(os.path.join(output_dir, project, Victim_md5)):
                    try:
                        Paired_Test = pd.read_csv(os.path.join(output_dir, project, Victim_md5, Test_md5))
                        if Paired_Test['id'][1] != Test_id:
                            match = 0
                            break
                        if victim_or_brittle == "Brittle" and Paired_Test['status'][0] == 'passed' and Paired_Test['status'][1] == 'passed':
                            count = count + 1
                            update_paired_tests(result_csv, Gruber_Metadata, Paired_Test, Conflict)
                        if victim_or_brittle == "Victim" and Paired_Test['status'][0] == 'passed' and Paired_Test['status'][1] != 'passed':
                            count = count + 1
                            update_paired_tests(result_csv, Gruber_Metadata, Paired_Test, Conflict)
                    except:
                        with open(error_log, 'a') as f:
                            f.write(victim_or_brittle + ',' + Victim_Hash[Victim_md5] + '\n')
                        continue
                if match == 1:
                    update_stat_for_paired_tests(stat_csv, Gruber_Metadata, Test_id, count, Conflict)
            print("\r%s %.2f %%" % (Info, numrow * 100 / total), end="")
        print("\r%s %.2f %%" % (Info, 100))

update("Brittle")
update("Victim")

