# python3 parser/polluter.py dataset_latest.csv parsing_result/isolated output/polluter parsing_result/polluter

from parseMethods import *
import sys

# dataset_path = "../dataset_latest.csv"
# victim_brittle = "../parsing_result/isolated"
# output_dir = "../output/polluter_tsm"
# result_dir = "../parsing_result/polluter_tsm"

dataset_path = sys.argv[0]
victim_brittle = sys.argv[1]
output_dir = sys.argv[2]
result_dir = sys.argv[3]

error_log = os.path.join(result_dir, 'Error.csv')
polluter_to_detect = os.path.join(result_dir, 'polluter_to_detect.csv')

Gruber = Gruber_init()
init(result_dir, error_log)

f = open(polluter_to_detect, 'w')
f.close()

def update(victim_or_brittle):
    test_list = os.path.join(victim_brittle, 'Brittle.csv') if victim_or_brittle == "Brittle" else os.path.join(victim_brittle, 'Victim.csv')
    result_csv = os.path.join(result_dir, 'state-setter-potential.csv') if victim_or_brittle == "Brittle" else os.path.join(result_dir, 'polluter-potential.csv')
    stat_csv = os.path.join(result_dir, 'state-setter-stat-potential.csv') if victim_or_brittle == "Brittle" else os.path.join(result_dir, 'polluter-stat-potential.csv')
    Info = "Detecting state-setters for brittles: " if victim_or_brittle == "Brittle" else "Detecting polluters for victims: "
    init_csv_for_paired_tests(result_csv)
    init_stat_csv_for_paired_tests(stat_csv)
    total = sum(1 for line in open(test_list)) - 1
    with open(test_list, 'rt') as f:
        num_row, num_valid, num_not_none = 0, 0, 0
        r = csv.reader(f)
        for row in r:
            Project, Test_id, Conflict = [row[0], row[1], row[2], row[3]], row[4], row[6]

            if Project[0] == "Project_Name":
                continue

            Gruber_key = Project[0]+'$'+Test_id
            Gruber_row = Gruber[Gruber_key]

            num_row += 1
            Victim_Hash = {}
            if not os.path.exists(os.path.join(output_dir, Project[0], 'victim_mapping.csv')):
                with open(polluter_to_detect, 'a') as f:
                    csv.writer(f).writerow(Gruber_row)
                continue
            with open(os.path.join(output_dir, Project[0], 'victim_mapping.csv'), 'rt') as f1:
                for row1 in f1:
                    Victim_Hash[row1[:-34]] = row1[-33:-1]

            try:
                Victim_md5 = Victim_Hash[Test_id]
            except:
                with open(polluter_to_detect, 'a') as f:
                    csv.writer(f).writerow(Gruber_row)
                continue

            num_valid += 1
            count = 0
            if len(os.listdir(os.path.join(output_dir, Project[0], Victim_md5))) == 0:
                with open(error_log, 'a') as f:
                    csv.writer(f).writerow(['TestNotRun', Project[0], Project[3], Test_id])
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
            print("\r%s %d / %d" % (Info, num_row, total), end="")
        print("\r%s %d / %d" % (Info, num_row, total))

    print("---------------------------------   Summary   ---------------------------------")
    print("%d OD tests are suspected-%s" % (total, "brittles" if victim_or_brittle == "Brittle" else "victims"))
    print("%d OD tests are not run by the script: check %s" % (total - num_valid, polluter_to_detect))
    print("%d OD tests are successfully run by the script" % (num_valid))
    print("    %d are not %s (have no %s)" % (num_valid-num_not_none, "brittles" if victim_or_brittle == "Brittle" else "victims", \
                                              "state-setter" if victim_or_brittle == "Brittle" else "polluter"))
    print("    %d have at least 1 %s" % (num_not_none, "state-setters" if victim_or_brittle == "Brittle" else "polluters"))
    print("    Check datailed stat in %s" % (stat_csv))

update("Brittle")
update("Victim")


"""
Result from the latest run:

Detecting state-setters for brittles:  744 / 744
---------------------------------   Summary   ---------------------------------
744 OD tests are suspected-brittles
0 OD tests are not run by the script: check ../parsing_result/polluter/polluter_to_detect.csv
744 OD tests are successfully run by the script
    354 are not brittles (have no state-setter)
    390 have at least 1 state-setters
    Check datailed stat in ../parsing_result/polluter/state-setter-stat-potential.csv
Detecting polluters for victims:  2236 / 2236
---------------------------------   Summary   ---------------------------------
2236 OD tests are suspected-victims
13 OD tests are not run by the script: check ../parsing_result/polluter/polluter_to_detect.csv
2223 OD tests are successfully run by the script
    1518 are not victims (have no polluter)
    705 have at least 1 polluters
    Check datailed stat in ../parsing_result/polluter/polluter-stat-potential.csv

"""
