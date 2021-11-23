import pandas as pd

vb = pd.read_csv("victims_brittles.csv")
print("{} OD tests in {} Projects are victims or brittles suggested in Gruber's dataset".format(len(vb), len(set(vb['Project_Name']))))

vb = pd.read_csv("output/victim_or_brittles.csv")
print("{} OD tests in {} Projects are run successfully in our environment".format(len(vb), len(set(vb['Project_Name']))))

victims = pd.read_csv("output/victims.csv")
print("\t{} OD tests in {} Projects are potential victims".format(len(victims), len(set(victims['Project_Name']))))



polluters_tcm = pd.read_csv("output/potential_polluters_tcm_stat.csv")
projects = []
have_polluter = []
for i in range(len(polluters_tcm)):
    if polluters_tcm['Stat_Polluter'][i]:
        projects.append(polluters_tcm['Project_Name'][i])
        have_polluter.append(polluters_tcm['Test_id'][i])
print("\t\t{} victims in {} Projects have polluters in TCM".format(len(have_polluter), len(list(set(projects)))))

cleaners = pd.read_csv("output/cleaner/cleaner_tcm.csv")
projects = []
have_cleaner = []
for i in range(len(cleaners)):
    projects.append(cleaners['Project_Name'][i])
    have_cleaner.append(cleaners['Victim'][i])
print("\t\t\t{} victims in {} Projects have cleaners in TCM".format(len(have_cleaner), len(list(set(projects)))))

polluters_tcm = pd.read_csv("output/potential_polluters_tsm_stat.csv")
projects = []
have_polluter = []
for i in range(len(polluters_tcm)):
    if polluters_tcm['Stat_Polluter'][i]:
        projects.append(polluters_tcm['Project_Name'][i])
        have_polluter.append(polluters_tcm['Test_id'][i])
print("\t\t{} victims in {} Projects have polluters in TSM".format(len(have_polluter), len(list(set(projects)))))

cleaners = pd.read_csv("output/cleaner/cleaner_tsm.csv")
projects = []
have_cleaner = []
for i in range(len(cleaners)):
    projects.append(cleaners['Project_Name'][i])
    have_cleaner.append(cleaners['Victim'][i])
print("\t\t\t{} victims in {} Projects have cleaners in TSM".format(len(have_cleaner), len(list(set(projects)))))



brittles = pd.read_csv("output/brittles.csv")
print("\t{} OD tests in {} Projects are potential brittles".format(len(brittles), len(set(brittles['Project_Name']))))

ss_tcm = pd.read_csv("output/potential_state_setters_tcm_stat.csv")
projects = []
have_ss = []
for i in range(len(ss_tcm)):
    if ss_tcm['Stat_State-setter'][i]:
        projects.append(ss_tcm['Project_Name'][i])
        have_ss.append(ss_tcm['Test_id'][i])
print("\t\t{} brittles in {} Projects have state-setters in TCM".format(len(have_ss), len(list(set(projects)))))

ss_tcm = pd.read_csv("output/potential_state_setters_tsm_stat.csv")
projects = []
have_ss = []
for i in range(len(ss_tcm)):
    if ss_tcm['Stat_State-setter'][i]:
        projects.append(ss_tcm['Project_Name'][i])
        have_ss.append(ss_tcm['Test_id'][i])
print("\t\t{} brittles in {} Projects have state-setters in TSM".format(len(have_ss), len(list(set(projects)))))



