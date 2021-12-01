# iFixFlakies_python
A shell script running iPFlakies to detect polluters of victims as well as state-setters for brittles in the dataset from Gruber et al.  

## How to run

Download the docker image: https://zenodo.org/record/5747276/files/python_ipflakies.tar?download=1

Download the pre-installed repositories for analysis: 

```
tar -xzvf Installed_Repositories.tar.gz

docker import - python_ipflakies < python_ipflakies.tar

docker run -it -v $(pwd):/home/user/data python_ipflakies /bin/bash

cd /home/user/iFixFlakies_python

# Run iDFlakies_python
bash main.sh dataset_trial.csv

# Run iFixFlakies_python
bash patcher.sh
```

Check output in `/home/user/iFixFlakies_python/repro` inside the docker container.

