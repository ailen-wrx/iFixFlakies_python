from parseMethods import *


def Gruber_init():
    Gruber = dict()
    with open(dataset_dir, 'rt') as f:
        r = csv.reader(f)
        for row in r:
            func = row[0] + '-' + row[3] + '::' + row[5]
            Gruber[func] = {'Project_Name': row[0],
                            'Project_URL': row[1],
                            'Project_Hash': row[2],
                            'Isolation': row[8]}
    return Gruber


def init_csv(fileName):
    with open(fileName, 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 'Test1', 'Message1',
                                'Test2', 'Message2', 'Script', 'Gruber'])


def log_init():
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    file = open(os.path.join(result_dir, 'Error.log'), 'w')
    file.close()
    with open(os.path.join(result_dir, 'Verdict_Isolated.csv'), 'w') as f:
        csv.writer(f).writerow(['Project_Name', 'Project_URL', 'Project_Hash', 'Test_id',
                                'Script', 'Gruber'])
    init_csv(os.path.join(result_dir, 'Pass-Fail.csv'))
    init_csv(os.path.join(result_dir, 'Pass-Pass.csv'))
    init_csv(os.path.join(result_dir, 'Fail-Pass.csv'))
    init_csv(os.path.join(result_dir, 'Fail-Fail.csv'))


log_init()
Gruber = Gruber_init()
parse_output_dir(Gruber)
