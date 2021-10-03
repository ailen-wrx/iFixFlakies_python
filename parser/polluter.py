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
        num_row, num_not_none = 0, 0
        r = csv.reader(f)
        for row in r:
            num_row += 1
            Project, Test_id, Conflict = [row[0], row[1], row[2], row[3]], row[4], row[6]
            Victim_Hash = {}
            if not os.path.exists(os.path.join(output_dir, Project[0], 'victim_mapping.csv')):
                continue
            with open(os.path.join(output_dir, Project[0], 'victim_mapping.csv'), 'rt') as f1:
                for row1 in f1:
                    Victim_Hash[row1[:-34]] = row1[-33:-1]

            try:
                Victim_md5 = Victim_Hash[Test_id]
            except:
                with open(error_log, 'a') as f:
                    csv.writer(f).writerow(['NotFound', Project[0], Project[3], Test_id])
                continue

            count = 0
            if len(os.listdir(os.path.join(output_dir, Project[0], Victim_md5))) == 0:
                with open(error_log, 'a') as f:
                    csv.writer(f).writerow(['NotRun', Project[0], Project[3], Test_id])
                continue

            for Test_md5 in os.listdir(os.path.join(output_dir, Project[0], Victim_md5)):
                try:
                    Paired_Test = pd.read_csv(os.path.join(output_dir, Project[0], Victim_md5, Test_md5))
                    if victim_or_brittle == "Brittle" and Paired_Test['status'][0] == 'passed' and Paired_Test['status'][1] == 'passed':
                        count = count + 1
                        update_paired_tests(result_csv, Project, Paired_Test, Conflict)
                    if victim_or_brittle == "Victim" and Paired_Test['status'][1] != 'passed':
                        count = count + 1
                        update_paired_tests(result_csv, Project, Paired_Test, Conflict)
                except:
                    with open(error_log, 'a') as f:
                        csv.writer(f).writerow(['ERROR', Project[0], Project[3], Test_id])
                    continue
            update_stat_for_paired_tests(stat_csv, Project, Test_id, count, Conflict)
            if count != 0:
                num_not_none += 1
            print("\r%s %d / %d" % (Info, num_row, total-1), end="")
        print("\r%s %d / %d" % (Info, num_row-1, total-1))

    print("---------------------------------   Summary   ---------------------------------")
    print("%d OD tests are suspected-%s" % (total-1, "brittles" if victim_or_brittle == "Brittle" else "victims"))
    print("    %d are not %s (have no %s)" % (total-1-num_not_none, "brittles" if victim_or_brittle == "Brittle" else "victims", \
                                              "state-setter" if victim_or_brittle == "Brittle" else "polluter"))
    print("    %d have at least 1 %s" % (num_not_none, "state-setters" if victim_or_brittle == "Brittle" else "polluters"))
    print("    Check datailed stat in %s" % (stat_csv))

update("Brittle")
update("Victim")

