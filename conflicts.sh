repo_dir=$1
conflict=$2
output_dir=$3


root_dir=$(pwd)
rm -rf $output_dir
mkdir -p $output_dir
for i in $(cat $conflict | sed '1d'); do
    project=$(echo $i | cut -d, -f1)
    testname=$(echo $i | cut -d, -f4)
    cd $repo_dir/$project
    python3 -m venv venv
    source venv/bin/activate
    for j in $(find -name "*requirement*"); do
	pip install -r $j
    done
    pip install pytest
    pip install pytest-csv
    md5=$(echo $i | md5sum | cut -d' ' -f1)
    mkdir -p $output_dir/$md5
    for k in {1..10}; do
        timeout 1000s pytest $testname --csv $output_dir/$md5/$k.csv
    done
    echo $md5,$i >> $output_dir/conflict_mapping.csv
    deactivate
done
