#bash clone.sh $(pwd)/dataset_amended.csv $(pwd)/Repo

dataset=$1
repo_dir=$2

echo script version: $(git rev-parse HEAD)

base_url=$(pwd)
mkdir -p $repo_dir/$project
rm $base_url/latest_repo_dirs.csv
for i in $(cut -d, -f1,2 $dataset | uniq | sed '1d'); do
    project=$(echo $i | cut -d, -f1)
    url=$(echo $i | cut -d, -f2)

    echo cloning $project starttime: $(date) >> log_clone

    cd $repo_dir

    if [ -x "$project" ]; then
        echo $project skipped.
	continue
    fi

    git clone $url --depth=1

    if [ ! -x "$project" ]; then
        continue
    fi

    cd $repo_dir/$project
    sha=$(grep $project, $dataset | cut -d, -f3 | head -1)
    echo Switching to $sha...
    git remote set-branches origin $sha
    git fetch --depth 1 origin $sha
    git checkout $sha

    pip freeze > requirements_freeze.txt
    cat requirements_freeze.txt

    rm -rf venv
    python3 -m venv venv

    source venv/bin/activate

    pip3 install --upgrade pip

    for i in $(find -maxdepth 1 -name "*requirement*"); do
        pip3 install -r $i
    done
    pip3 install -r requirements_freeze.txt

    pip3 install pytest
    pip3 install pytest-csv

    python -m pytest --collect-only -q > test_list

    deactivate
    
    cd $base_url
done
