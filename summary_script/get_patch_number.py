import csv

patch_brittle="C:/Users/LENOVO/Desktop/tmp_brittle_result.csv"
#patch_tsm='C:/Users/LENOVO/Desktop/cleaner_tsm_patch_updated.csv'
#patch_tcm='C:/Users/LENOVO/Desktop/final_cleaner_tcm_patch.csv'
victim_patch_save='D:/save_new_2.csv'
origin_brittle='C:/Users/LENOVO/Documents/WeChat Files/wxid_36u7rqtf25ci12/FileStorage/File/2021-11/temp.csv'


all_victims=[]
save_victims=[]
fixed_victims=[]
fixed_projects=[]
project=[]
good_list=[]
all_b=[]
passed_b=[]
failed_sb=[]
all_b_o=[]

def get_fixed_tests(patch_tsm,csv_writer):
    csv_reader = csv.reader(open(patch_tsm))

    for eachrow in csv_reader:
        #all_victims.append(eachrow[3])
        if eachrow[0] != 'project':
            project.append(eachrow[0])
            all_victims.append(eachrow[3])
            if (len(eachrow)>6) and eachrow[0]!='project':
                if (eachrow[5]=='failed' and eachrow[6]=='passed') or (eachrow[5]=='error' and eachrow[6]=='passed'):
                    good_list.append(eachrow[3])
                if eachrow[5]=='passed':
                    passed_b.append(eachrow[3])
                if eachrow[6]!='passed':
                    failed_sb.append(eachrow[3])
                if eachrow[9]!='':
                    #print(eachrow[9])
                    fixed_victims.append(eachrow[3])
                    fixed_projects.append(eachrow[0])
                    if eachrow[3] not in save_victims:
                        record_result=[eachrow[0],eachrow[1],eachrow[3],eachrow[4],eachrow[7],eachrow[11],eachrow[10]]
                        csv_writer.writerow(record_result)
                        save_victims.append(eachrow[3])
                else:
                    if eachrow[3] not in save_victims:
                        record_result = [eachrow[0], eachrow[1], eachrow[3], eachrow[5], eachrow[6]]
                        csv_writer.writerow(record_result)
                        save_victims.append(eachrow[3])
            else:

                    if eachrow[3] not in save_victims:
                        record_result = [eachrow[0], eachrow[1], eachrow[3],eachrow[4]]
                        csv_writer.writerow(record_result)
                        save_victims.append(eachrow[3])



    #print(list(set(fixed_victims)))

with open(victim_patch_save,"w",newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["project", "SHA", "victim", "pv_result", "pcv_result", "patch", "minimal patch time"])
    get_fixed_tests(patch_brittle,csv_writer)
    print(len(list(set(all_b))))
    print(len(list(set(all_victims))), len(list(set(fixed_victims))),len(save_victims))
    print(len(list(set(project))))
    print(len(list(set(fixed_projects))))
    print(len(list(set(good_list))))
    print(len(list(set(passed_b))))
    print(len(list(set(failed_sb))))
    print(len(list(set(passed_b+failed_sb))))
    print(len(list(set(all_b_o))))
