from parseMethods import *

with open("../dataset_amended.csv", 'w') as f:
    csv.writer(f).writerow(['Project_Name','Project_URL','Project_Hash','Test_filename','Test_classname','Test_funcname','Test_parametrization','Order-dependent','Verdict_Isolated','Verdict_OriginalOrder'])

with open("../victims_brittles", 'rt') as f:
    r = csv.reader(f)
    for row in r:
        project = row[0]
        if project == 'Project_Name':
            continue
        Test_filename = row[3]
        Test_classname = row[4]
        Test_funcname = row[5]
        Test_para = row[6]

        if str(Test_filename).split('/')[-1] != (str(Test_classname).split('.')[-1] + '.py'):
            ClassName = str(Test_classname).split('.')
            ClassName[-2] = ClassName[-2] + ".py"
            row[3] = '/'.join(ClassName[:-1])
            row[4] = ClassName[-1]
        else: 
            row[4] = ''
        with open(dataset_amended, 'a') as f1:
            csv.writer(f1).writerow(row)

