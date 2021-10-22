from parseMethods import *

Gruber = Gruber_init()


def patch(file_input, file_output):
    with open(file_input, 'rt') as f:
        r = csv.reader(f)
        for (row) in r:
            Project_Name = row[0]

            if (Project_Name == "Project_Name"):
                row.append("Test_classname")
                with open(file_output, 'w') as f1:
                    csv.writer(f1).writerow(row)

                continue
            
            Test_id = row[4]
            Gruber_key = Project_Name+'$'+Test_id
            Gruber_row = Gruber[Gruber_key]
            row.append(Gruber_row[4])

            with open(file_output, 'a') as f1:
                csv.writer(f1).writerow(row)

patch("../parsing_result/isolated/Victim.csv", "../parsing_result/isolated/Victim_patched.csv")
patch("../parsing_result/isolated/Brittle.csv", "../parsing_result/isolated/Brittle_patched.csv")












                                
