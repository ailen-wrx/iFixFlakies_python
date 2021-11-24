import pandas as pd

vb = pd.read_csv("victims_brittles.csv")
print("{} OD tests in {} Projects are victims or brittles suggested in Gruber's dataset".format(len(vb), len(set(vb['Project_Name']))))

vb = pd.read_csv("master/src/victim_or_brittles.csv")
print("{} OD tests in {} Projects are run successfully in our environment".format(len(vb), len(set(vb['Project_Name']))))

nond = pd.read_csv("master/src/non-deterministic.csv")
print("\t{} OD tests in {} Projects are non-deterministic".format(len(nond), len(set(nond['Project_Name']))))

victims = pd.read_csv("master/src/victims.csv")
print("\t{} OD tests in {} Projects are potential victims".format(len(victims), len(set(victims['Project_Name']))))


polluters = pd.read_csv("master/src/polluters_stat.csv")
projects = []
have_polluter = []
for i in range(len(polluters)):
    if polluters['Stat_Polluter'][i]:
        projects.append(polluters['Project_Name'][i])
        have_polluter.append(polluters['Test_id'][i])
print("\t\t{} victims in {} Projects have polluters".format(len(have_polluter), len(list(set(projects)))))

cleaners = pd.read_csv("master/src/cleaners.csv")
projects = []
have_cleaner = []
for i in range(len(cleaners)):
    projects.append(cleaners['Project_Name'][i])
    have_cleaner.append(cleaners['Victim'][i])
print("\t\t\t{} victims in {} Projects have cleaners".format(len(set(have_cleaner)), len(list(set(projects)))))


brittles = pd.read_csv("master/src/brittles.csv")
print("\t{} OD tests in {} Projects are potential brittles".format(len(brittles), len(set(brittles['Project_Name']))))

ss_tcm = pd.read_csv("master/src/state_setters_stat.csv")
projects = []
have_ss = []
for i in range(len(ss_tcm)):
    if ss_tcm['Stat_State-setter'][i]:
        projects.append(ss_tcm['Project_Name'][i])
        have_ss.append(ss_tcm['Test_id'][i])
print("\t\t{} brittles in {} Projects have state-setters in TCM".format(len(have_ss), len(list(set(projects)))))


