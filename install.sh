repo_dir=$1
project=$2
dataset=$3
test_list=$4
output_dir=$5
task_type=$6

cd $repo_dir/$project
rm -rf venv
python3 -m venv venv
source venv/bin/activate
for i in $(find -maxdepth 1 -name "*requirement*"); do
    pip3 install -r $i
done
pip3 install pytest
pip3 install pytest-csv

pytest --collect-only -q > $test_list
cd -
rm -rf $output_dir/$project
mkdir -p $output_dir/$project

for i in $(grep $project, $dataset); do
    Test_filename=$(echo $i | cut -d, -f4)
    Test_classname=$(echo $i | cut -d, -f5)
    Test_funcname=$(echo $i | cut -d, -f6)
    Test_parametrization=$(echo $i | cut -d, -f7)

    if [[ $Test_parametrization == '' ]]; then
        victim=$(grep $Test_filename:: $repo_dir/$project/$test_list | grep ::$Test_funcname | sort | head -1)
    else
        victim=$(grep $Test_filename:: $repo_dir/$project/$test_list | grep ::$Test_funcname | grep $Test_parametrization | sort | head -1)
    fi

    if [[ -z "$victim" ]]; then
        continue
    fi

    md5=$(echo $i | md5sum | cut -d' ' -f1)
    echo $victim,$(date) >> $output_dir/$project/log_pytest.csv
    echo $victim,$md5 >> $output_dir/$project/victim_mapping.csv

    if [[ $task_type == 1 ]]; then
        bash verdict_isolated.sh $victim $test_list $Test_filename $repo_dir/$project $output_dir/$project/$md5
    fi

    if [[ $task_type == 2 ]]; then
        bash find_polluter.sh $victim $test_list $Test_filename $repo_dir/$project $output_dir/$project/$md5
    fi

    if [[ $task_type == 3 ]]; then
        continue
    fi
    
done
deactivate
rm -rf $repo_dir/$project/venv
