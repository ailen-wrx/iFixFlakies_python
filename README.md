# iFixFlakies_python
A shell script running `pytest` to detect polluters of victims in the dataset from Gruber et al.  

## Directory Structure
```
iFixFlakies_python    
├── batch.sh  
├── clone.sh  
├── find_polluter.sh  
├── install.sh  
├── output       /* where the results are saved */  
├── README.md  
├── Repo         /* where the cloned repos are located */  
│   ├── $project1 
│   │   ├── ...  /* project code */  
│   │   ├── requirements.txt  
│   │   └── test_list  /* a list of all test functions in this project */  
│   ├── $project2
│   │
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
`$ curl -o victims_brittles.csv https://zenodo.org/record/4450435/files/victims_brittles.csv?download=1`

### Cloning projects
`$ bash clone.sh victims_brittles.csv $(pwd)/Repo`  
All 608 projects will be cloned under direcroty `Repo`.  

### Detecting polluters
**on a single project**  
`$ bash install.sh $(pwd)/Repo $project_name $(pwd)/victims_brittles.csv $test_list $(pwd)/output`

While running `install.sh` on each project, the result data will be stored in a directory under `output`:
```
iFixFlakies_python / output
├── stat.csv
├── $project1
│   ├── c68022abd1d6ebb2f9ec183d506799b7
│   │   ├── 117c166fbcee8fa7f9bb4ecff9736c3a.csv
│   │   ├── ......
│   │   └── test_mapping.csv
│   ├── f5eed40f2f6735bfe5e3cdc72d5d1400
│   │   ├── 117c166fbcee8fa7f9bb4ecff9736c3a.csv
│   │   ├── ......
│   │   └── test_mapping.csv
│   └── victim_mapping.csv
├── $project2
│
```
For each victim test detected in dataset from Gruber et al, one directory will be generated to store the test result of `pytest $test_i $victim`, where `$test_i` calls for every test function in the same test class with `victim`. If `$test_i` passes while `$victim` fails, the `$test_i` is regarded as a polluter.

**on a batch of projects**  
`$ bash batch.sh $(pwd)/victims_brittles.csv $(pwd)/Repo $(pwd)/output test_list`

If a project does not exist, or the script fails run `pytest` on the project, such information wil be recorded in `stat.csv`.

Inside `stat.csv`, there are 3 states for each project:
 - `fail_to_clone`: fail to find the repository on GitHub, or the project is renamed.
 - `requirements_not_found`: fail to detect something like `requirements.txt` to install neccesary dependencies for running `pytest` on the project.
 - `install`: successfully install the requirements and run `pytest` on specified tests, with several unexpected situations still included.
 
 



