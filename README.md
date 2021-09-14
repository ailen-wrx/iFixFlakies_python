# iFixFlakies_bash
A shell script running `pytest` to detect polluters of victims in the dataset from Gruber et al.

## Directory Structure
.
├── clone.sh
├── find_polluter.sh
├── install.sh
├── output
├── README.md
├── Repo
│   └── abagen
│       ├── # project code #
│       ├── requirements.txt
│       └── tests.csv
└── victims_brittles.csv

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
`$ bash clone.sh victims_brittles.csv Repo`

### Detecting polluters
on single project
`$ bash install.sh Repo $project_name$ victims_brittles.csv tests.csv output`

on a batch of projects
`$ bash batch.sh $(pwd)/victims_brittles.csv Repo $(pwd)/output`


