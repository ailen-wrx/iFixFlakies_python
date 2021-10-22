
from parseMethods import *

output_dir = "../output/cleaner"
mapping = "../output/cleaner/polluter-victim-mapping.csv"
result_dir = "../parsing_result/cleaner"

if not os.path.exists(result_dir):
    os.makedirs(result_dir)

with open(os.path.join(result_dir, 'cleaners.csv'), 'w') as f:
    csv.writer(f).writerow(['Project', 'URL', 'SHA', 'Polluter', 'Cleaner', 'Victim'])

with open(os.path.join(result_dir, 'cleaners_stat.csv'), 'w') as f:
        csv.writer(f).writerow(['Project', 'URL', 'SHA', 'Polluter', 'Victim', '#Cleaners'])

Gruber = Gruber_init()
        
with open(mapping, 'rt') as f1:
    r1 = csv.reader(f1)
    for row1 in r1:
        md5_polluter_victim = row1[0]
        Project = row1[1]
        Polluter = row1[2]
        Victim = row1[3]

        Gruber_key = Project+'$'+Victim
        row = Gruber[Gruber_key]

        Project_URL = row[1]
        Project_SHA = row[2]
        
        polluter_count = 0
        with open(os.path.join(output_dir, md5_polluter_victim, 'test_mapping.csv')) as f2:
            r2 = csv.reader(f2)
            for row2 in r2:
                md5_test = row2[0]
                Test = row2[1]

                Triple_Test = pd.read_csv(os.path.join(output_dir, md5_polluter_victim, md5_test+'.csv'))
                if Triple_Test['status'][0] == 'passed' and Triple_Test['status'][1] == 'passed' and Triple_Test['status'][2] == 'passed':
                    with open(os.path.join(result_dir, 'cleaners.csv'), 'a') as f:
                        csv.writer(f).writerow([Project, Project_URL, Project_SHA, Polluter, Test, Victim])
                        polluter_count += 1
                        
            with open(os.path.join(result_dir, 'cleaners_stat.csv'), 'a') as f:
                csv.writer(f).writerow([Project, Project_URL, Project_SHA, Polluter, Victim, polluter_count])


