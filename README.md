# iFixFlakies_python
Experimental scripts for running iPFlakies to detect polluters of victims as well as state-setters for brittles in the dataset from [Gruber et al.](https://www.computer.org/csdl/proceedings-article/icst/2021/683600a148/1tRP8lWaACc).

## Setup
To setup the environment,

 - download the docker image and pre-installed repositories for analysis to the current work folder:
    https://zenodo.org/record/5747276/files/python_ipflakies.tar?download=1

    https://zenodo.org/record/5748460/files/Installed_Repositories_part.zip?download=1
    https://zenodo.org/record/5748511/files/Installed_Repositories_part.z01?download=1

 - unzip the files and create docker container:
    ```
    cat Installed_Repositories_part.* > Installed_Repositories.zip

    unzip Installed_Repositories.zip > /dev/null

    docker import - python_ipflakies < python_ipflakies.tar

    docker run -it -v $(pwd):/home/user/data python_ipflakies /bin/bash
    
    cd /home/user/iFixFlakies_python
    ```


## How to run

```
# select dataset from one certain repository
echo "Project_Name,Project_URL,Project_Hash,Test_filename,Test_classname,Test_funcname,Test_parametrization,Order-dependent,Verdict_Isolated,Verdict_OriginalOrder" > dataset_demo.csv
# select dataset from one certain repository
grep ${project_name} dataset_final.csv >> dataset_demo.csv

# Run iDFlakies_python
bash main.sh dataset_demo.csv

# Run iFixFlakies_python
bash patcher.sh
```

Check output in `/home/user/iFixFlakies_python/repro` inside the Docker container.

### Example: `omersaraf/IOCynergy`
```
$ echo "Project_Name,Project_URL,Project_Hash,Test_filename,Test_classname,Test_funcname,Test_parametrization,Order-dependent,Verdict_Isolated,Verdict_OriginalOrder" > dataset_demo.csv
$ grep IOCynergy dataset_final.csv >> dataset_demo.csv

$ time bash main.sh dataset_demo.csv
# omit bash output
real    1m39.690s
user    1m23.305s
sys     0m20.948s

$ time bash patcher.sh
# omit bash output
real    0m26.594s
user    0m31.330s
sys     0m19.354s
```

Output of iDFlakies_python: `repro/Test_status.csv`

Output of iFixFlakies_python: `repro/patch_brittles.csv`, `repro/patch_victims.csv`

Patch files: `SAVE/`


