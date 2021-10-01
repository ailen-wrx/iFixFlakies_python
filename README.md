# iFixFlakies_python
A shell script running `pytest` to detect polluters of victims as well as state-setters for brittles in the dataset from Gruber et al.  

## Directory Structure
```
iFixFlakies_python    
├── batch.sh  
├── clone.sh  
├── find_cleaner.sh  
├── find_polluter.sh  
├── install.sh  
├── output       /* where the results are saved */  
│   ├── isolated  
│   ├── polluter
│   └── cleaner
├── parser/
├── README.md  
├── Repo         /* where the cloned repos are located */  
│   ├── $project1 
│   │   ├── ...  /* project code */  
│   │   ├── requirements.txt  
│   │   └── test_list  /* a list of all test functions in this project */  
│   ├── $project2
│  
├── verdict_isolated.sh  
└── victims_brittles.csv  
```

## How to Run

### Requirements
```
python3
python3-pip
pip install pytest
curl
```

### The dataset from Gruber et al.
```
$ curl -o victims_brittles.csv https://zenodo.org/record/4450435/files/victims_brittles.csv?download=1`
```

### Cloning projects
```
$ bash clone.sh $(pwd)/victims_brittles.csv $(pwd)/Repo
```  
608 projects will be cloned under direcroty `Repo`, as well as switching to current SHA.  

### Running pytest suites
| task     | task_type | task description |
| -------- | --------- | ------------------------------------------------------------ |
| isolated | 1         | To run each victim in isolation to decide it is a victim or brittle; |
| polluter | 2         | To run paired tests and find polluters for each victim;      |
| cleaner  | 3         | To run triple tests and find cleaners for each polluter-victim pair. |


**on a single project**  
`$ bash install.sh $(pwd)/Repo $project_name $(pwd)/victims_brittles.csv $test_list $(pwd)/output/$task $task_type`  
example:   
```
$ bash install.sh $(pwd)/Repo abagen $(pwd)/victims_brittles.csv test_list $(pwd)/output/isolated 1
$ bash install.sh $(pwd)/Repo abagen $(pwd)/victims_brittles.csv test_list $(pwd)/output/polluter 2
$ bash install.sh $(pwd)/Repo abagen $(pwd)/victims_brittles.csv test_list $(pwd)/output/cleaner  3
```  
  
While running `install.sh` on each project, the result data will be stored in a directory under `output`:  
```
iFixFlakies_python / output / polluter (or isolated or cleaner)
├── stat.csv
├── $project1
│   ├── c68022abd1d6ebb2f9ec183d506799b7
│   ├── f5eed40f2f6735bfe5e3cdc72d5d1400
│   ├── ...
│   ├── log_pytest.csv
│   └── victim_mapping.csv
├── $project2

* log_pytest.csv: Records the time at which each victim is tested,
* victim_mapping.csv: Records the mapping between names of directories in MD5sum and victims
```
  
Inside each MD5sum-named directory, the raw data varies depending on different tasks.  
 1. isolated
 ```
 iFixFlakies_python / output / isolated
 ├── stat.csv
 ├── $project1
 │   ├── c68022abd1d6ebb2f9ec183d506799b7
 │   │   ├── 1.csv
 │   │   ├── ...
 │   │   ├── 10.csv
 │   │   └── timed_out.csv
 │   ├── f5eed40f2f6735bfe5e3cdc72d5d1400
 │   
 ```
 For each test detected in dataset from Gruber et al, run `pytest $test` individually for 10 times, exporting the test results to `csv` files. `timed_out.csv` records the tests which are run for over 1000 seconds without pass or fail. The test is grouped by the overall appearance of these 10 tests. If they all pass, the test is regarded as a victim, otherwise a brittle.  

 2. polluter 
 ```
 iFixFlakies_python / output / polluter
 ├── stat.csv
 ├── $project1
 │   ├── c68022abd1d6ebb2f9ec183d506799b7
 │   │   ├── 4438dee69b3d0f486a012a884f7ef92b.csv
 │   │   ├── a8ea570511cc44c6ebdbab76d339f917.csv
 │   │   ├── ...
 │   │   └── timed_out.csv
 │   ├── f5eed40f2f6735bfe5e3cdc72d5d1400
 │   
 ```
 For each test, run `pytest $i $test`, where `$i` calls for all other test functions under the same test class with `$test`, exporting the test results to `csv` files. If `$i` passes while `$test(as a victim)` fails, the `$i` is regarded as a polluter. If `$i` passes while `$test(as a brittle)` passes, the `$i` is regarded as a state-setter.  

 3. cleaner

**on a batch of projects**  
On our Azure server:  
`$ bash batch.sh $(pwd)/victims_brittles.csv $(pwd)/Repo $(pwd)/output/$task $test_list $task_type 1 ~/compiled-projects-w-deps/pod-results/$task`  
example:   
```
$ bash batch.sh $(pwd)/victims_brittles.csv $(pwd)/Repo $(pwd)/output/isolated test_list 1 1 ~/compiled-projects-w-deps/pod-results/isolated
$ bash batch.sh $(pwd)/victims_brittles.csv $(pwd)/Repo $(pwd)/output/polluter test_list 2 1 ~/compiled-projects-w-deps/pod-results/polluter
$ bash batch.sh $(pwd)/victims_brittles.csv $(pwd)/Repo $(pwd)/output/cleaner  test_list 3 1 ~/compiled-projects-w-deps/pod-results/cleaner
```  

To run locally:  
`$ bash batch.sh $(pwd)/victims_brittles.csv $(pwd)/Repo $(pwd)/output/$task $test_list $task_type 0 $(pwd)`  
example: 
```
$ bash batch.sh $(pwd)/victims_brittles.csv $(pwd)/Repo $(pwd)/output/isolated test_list 1 0 $(pwd)`
```
  
If a project does not exist, or the script fails to run `pytest` on the project, such information wil be recorded in `stat.csv`.  
Inside `stat.csv`, there are 3 states for each project:
 - `fail_to_clone_or_project_renamed`: fail to clone the repository from GitHub, or the project is renamed(then the script fails to locate the project with the outdated project name provided by Gruber dataset).
 - `requirements_not_found`: fail to detect something like `requirements.txt` to install neccesary dependencies for running `pytest` on the project.
 - `install`: successfully install the requirements and run `pytest` on specified tests, with several unexpected situations still to be handled by the python scripts in `parser/`.
 
 
### Summarizing raw data with python scripts
```
cd parser
python3 isolated.py 
python3 polluter.py
```