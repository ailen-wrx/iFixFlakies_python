import os
import sys
import csv
import traceback

tcm = sys.argv[1]
output_dir = sys.argv[2]
if tcm == "1":
    flg = "tcm"
else:
    flg = "tsm"

output_polluter = os.path.join(output_dir, "potential_polluters_{}.csv".format(flg))
output_polluter_stat = os.path.join(output_dir, "potential_polluters_{}_stat.csv".format(flg))
output_ss = os.path.join(output_dir, "potential_state_setters_{}.csv".format(flg))
output_ss_stat = os.path.join(output_dir, "potential_state_setters_{}_stat.csv".format(flg))

TASK = "polluter_{}".format(flg)
VICTIM = "victims"
BRITTLE = "brittles"

def process(victim_or_brittle):
    errors = os.path.join(output_dir, "errors_{}_{}.csv".format(victim_or_brittle, flg))
    dataset = os.path.join(output_dir, "{}.csv".format(victim_or_brittle))

    output_file = output_polluter if victim_or_brittle == VICTIM else output_ss
    output_stat_file = output_polluter_stat if victim_or_brittle == VICTIM else output_ss_stat

    polluter_or_ss = "Polluter" if victim_or_brittle == VICTIM else "State-setter"

    tot = sum(1 for row in csv.reader(open(dataset, 'rt')))
    with open(dataset, 'rt') as fds, \
        open(output_file, 'w') as output, \
        open(output_stat_file, 'w') as output_stat, \
        open(errors, 'w') as errorfile :

        for i, row in enumerate(csv.reader(fds)):
            print("\r{} / {}".format(i, tot), end="")
            Project = row[0]
            Project_URL = row[1]
            Project_Hash = row[2]
            Test_id = row[3]
            Verdict = row[4]

            if Project == "Project_Name":
                csv.writer(output).writerow(["Project_Name", "Project_URL", "Project_Hash", "Test_id", "Duration_1", polluter_or_ss, "Duration_2"])
                csv.writer(output_stat).writerow(["Project_Name", "Project_URL", "Project_Hash", "Test_id", "Stat_"+polluter_or_ss])
                continue

            try:
                victim_mapping = dict()
                count = 0
                with open(os.path.join(output_dir, TASK, Project, "victim_mapping.csv")) as f1:
                    for row1 in csv.reader(f1):
                        victim_mapping[row1[0]] = row1[1]
                    for i in os.listdir(os.path.join(output_dir, TASK, Project, victim_mapping[Test_id])):
                        try: 
                            csvdir = os.path.join(output_dir, TASK, Project, victim_mapping[Test_id], i)
                            testid = []
                            status = []
                            duration = []
                            with open(csvdir, 'rt') as fcsv:
                                for row2 in csv.reader(fcsv):
                                    testid.append(row2[0])
                                    status.append(row2[6])
                                    duration.append(row2[8])
                                if len(testid) <=2:
                                    continue
                            if (status[-1] != "passed" and victim_or_brittle == VICTIM) or \
                            (status[-1] == "passed" and victim_or_brittle == BRITTLE):
                                time2 = sum([float(x) for x in duration[1:-1]])
                                time1 = duration[-1]
                                csv.writer(output).writerow([Project, Project_URL, Project_Hash, Test_id, time1, testid[1], time2])
                                count += 1
                        except:
                            continue
                
                csv.writer(output_stat).writerow([Project, Project_URL, Project_Hash, Test_id, count])
                continue
                
            except Exception as e:
                traceback.print_exc()
                csv.writer(errorfile).writerow(row)
                continue


print(flg)          
process("victims")
process("brittles")
